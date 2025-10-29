import os
import re
import numpy as np
import wfdb
from scipy import signal
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import joblib 

# --- 1. Configuration --- 
DATA_DIR = r' ' # Path the Data Set is Saved
SAMPLING_RATE = 128
TARGET_FREQUENCIES = [6.66, 7.5, 8.57, 10.0, 12.0]
OCCIPITAL_CHANNELS = ['O1', 'O2']

# --- HELPER FUNCTIONS ---

def get_all_record_paths(directory):
    try:
        files = os.listdir(directory)
        if not files:
            print(f"DEBUG: The directory '{directory}' is empty or does not exist.")
            return []
        record_basenames = sorted(list(set([f.split('.')[0] for f in files if '.dat' in f])))
        return [os.path.join(directory, basename) for basename in record_basenames]
    except FileNotFoundError:
        print(f"DEBUG: The directory '{directory}' was not found. Please check the DATA_DIR path.")
        return []

def extract_features_and_labels(record_path):
    features = []
    labels = []
    try:
        record = wfdb.rdrecord(record_path)
        annotation = wfdb.rdann(record_path, 'win')
        channel_indices = [record.sig_name.index(ch) for ch in OCCIPITAL_CHANNELS]
        for i in range(0, len(annotation.sample), 2):
            start_sample = annotation.sample[i]
            end_sample = annotation.sample[i+1]
            trial_segment = record.p_signal[start_sample:end_sample, :]
            label_str_list = re.findall(r'(\d+\.?\d*)', annotation.aux_note[i])
            if not label_str_list:
                continue
            label = float(label_str_list[0])
            if label not in TARGET_FREQUENCIES:
                continue
            psd_features_for_trial = []
            for ch_idx in channel_indices:
                channel_data = trial_segment[:, ch_idx]
                freqs, psd = signal.welch(channel_data, fs=SAMPLING_RATE, nperseg=SAMPLING_RATE*2)
                for target_freq in TARGET_FREQUENCIES:
                    freq_idx = np.argmin(np.abs(freqs - target_freq))
                    psd_features_for_trial.append(psd[freq_idx])
            features.append(psd_features_for_trial)
            labels.append(label)
    except Exception as e:
        print(f"Could not process {os.path.basename(record_path)}. Error: {e}")
    return features, labels

# --- 2. Main Execution ---

if __name__ == "__main__":
    all_features = []
    all_labels = []

    print(f"DEBUG: Current working directory is: '{os.getcwd()}'")
    print(f"DEBUG: Looking for data in: '{os.path.abspath(DATA_DIR)}'")

    record_paths = get_all_record_paths(DATA_DIR)

    if not record_paths:
        print("\nERROR: No record paths were found.")
    else:
        print(f"\nFound {len(record_paths)} record files to process...")
        for path in record_paths:
            if os.path.basename(path).endswith('x'):
                print(f"-> Skipping adaptation file: {os.path.basename(path)}")
                continue
            features, labels = extract_features_and_labels(path)
            if features:
                all_features.extend(features)
                all_labels.extend(labels)
                print(f"-> Processed {os.path.basename(path)}: Found {len(labels)} trials.")
            else:
                print(f"-> Processed {os.path.basename(path)}: No valid trials found.")

    print("\nTotal trials collected:", len(all_labels))
    
    # --- 3. Label Encoding and Data Preparation ---

    if len(all_labels) > 0:
        X = np.array(all_features)
        le = LabelEncoder()
        y = le.fit_transform(all_labels)
        
        print("\nLabels have been encoded.")
        for i, class_name in enumerate(le.classes_):
            print(f"  - Frequency {class_name} Hz is now class {i}")

        # --- 4. Model Training and Evaluation ---

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        print(f"\nTraining data shape: {X_train.shape}")
        print(f"Testing data shape: {X_test.shape}")
        print("\nTraining Random Forest model...")
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nModel Training Complete!")
        print(f"   Accuracy on Test Set: {accuracy:.2%}")

        # --- 5. Visualization ---

        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=le.classes_, yticklabels=le.classes_)
        plt.title('Confusion Matrix')
        plt.ylabel('True Label (Frequency in Hz)')
        plt.xlabel('Predicted Label (Frequency in Hz)')
        
        # --- CORRECTED PLACEMENT FOR SAVING THE MODEL ---
        model_filename = 'ssvep_random_forest_model.joblib'
        label_encoder_filename = 'ssvep_label_encoder.joblib'

        joblib.dump(model, model_filename)
        joblib.dump(le, label_encoder_filename)

        print(f"\nModel saved to {model_filename}")
        print(f"Label encoder saved to {label_encoder_filename}")
        
        plt.show()
    else:
        print("\nNo data was collected. Model training skipped.")