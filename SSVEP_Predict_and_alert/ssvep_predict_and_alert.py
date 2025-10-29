import serial
import time
import joblib
import numpy as np
import os
import statistics
from scipy import signal
import wfdb

# ---------------------- CONFIGURATION ----------------------

SERIAL_PORT = ''       # ESP32 COM port
BAUD_RATE = 115200
MODEL_PATH = ' ' # Path the Model Saved in
LABEL_ENCODER_PATH = ' ' # Path The Label Saved in
INPUT_FILE = r' ' # Path the Input Test File is Saved in
SAMPLING_RATE = 128
TARGET_FREQUENCIES = [6.66, 7.5, 8.57, 10.0, 12.0]
OCCIPITAL_CHANNELS = ['O1', 'O2']

# ------------------------------------------------------------

# ---------------------- FEATURE EXTRACTION -----------------

def extract_features_from_file(record_path):
    """
    Extract PSD features from EEG record
    """
    features = []
    try:
        record = wfdb.rdrecord(record_path)
        annotation = wfdb.rdann(record_path, 'win')
        channel_indices = [record.sig_name.index(ch) for ch in OCCIPITAL_CHANNELS]

        for i in range(0, len(annotation.sample), 2):
            start_sample = annotation.sample[i]
            end_sample = annotation.sample[i+1]
            trial_segment = record.p_signal[start_sample:end_sample, :]

            psd_features = []
            for ch_idx in channel_indices:
                channel_data = trial_segment[:, ch_idx]
                freqs, psd = signal.welch(channel_data, fs=SAMPLING_RATE, nperseg=SAMPLING_RATE*2)
                for target_freq in TARGET_FREQUENCIES:
                    idx = np.argmin(np.abs(freqs - target_freq))
                    psd_features.append(psd[idx])
            features.append(psd_features)
    except Exception as e:
        print(f"Could not process {record_path}. Error: {e}")
    
    return np.array(features)

# ------------------------------------------------------------

# ---------------------- CONNECT TO ESP32 ------------------

print(f"Connecting to {SERIAL_PORT}...")
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
time.sleep(2)
print("Connected to ESP32. Waiting for it to signal readiness...")

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode(errors='ignore').strip()
        print("Received from ESP32:", line)
        if "ESP32_Ready" in line:
            print("ESP32 is ready. Proceeding with prediction.")
            break

# ------------------------------------------------------------

# ---------------------- LOAD MODEL ------------------------

print(f"\nLoading model from '{MODEL_PATH}'...")
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)

# ---------------------- EXTRACT FEATURES ------------------
X_new = extract_features_from_file(INPUT_FILE)
if X_new.shape[0] == 0:
    print("No valid trials found in input file. Exiting...")
    ser.close()
    exit()

pred_labels = model.predict(X_new)
pred_freqs = label_encoder.inverse_transform(pred_labels)

print("\n--- Individual Trial Predictions ---")
for i, freq in enumerate(pred_freqs, 1):
    print(f"  Trial #{i}: Predicted Frequency = {freq} Hz")

final_freq = statistics.mode(pred_freqs)
print("\n-------------------------------------------")
print(f"Final Predicted Frequency (Majority Vote): {final_freq} Hz")
print("-------------------------------------------")

# ---------------------- SEND TO ESP32 ---------------------

print(f"\nSending '{final_freq}' to ESP32...")
ser.write((str(final_freq) + '\n').encode())
time.sleep(1)

print("Waiting for ESP32 responses (this may take a few seconds)...")
sms_status_received = False

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode(errors='ignore').strip()
        print("ESP32 Response:", line)

        if "PYTHON_ALERT:SMS_SENT" in line:
            print("Python detected: SMS was successfully sent!")
            sms_status_received = True

        elif "PYTHON_ALERT:SMS_FAILED" in line:
            print("Python detected: SMS sending failed.")
            sms_status_received = True

        elif "Action complete" in line:
            break

    # Optional: add a timeout to avoid infinite loop
    time.sleep(0.1)

if not sms_status_received:
    print("Warning: Did not detect SMS status from ESP32.")

ser.close()
print("Serial connection closed.")
