# SSVEP-Based Patient Assistance System

A **Brain–Computer Interface (BCI)** system designed to assist paralyzed or motor-impaired patients in communicating essential needs using **Steady-State Visual Evoked Potentials (SSVEP)** and **IoT automation**.

This project bridges **EEG signal decoding** with **real-time patient alerting** via an **ESP32 microcontroller** — capable of sending **SMS notifications**, activating **LED indicators**, and **buzzers** for immediate assistance.


## Project Overview

Patients focus on one of several flickering light sources, each blinking at a unique frequency.  
The EEG headset captures the brain’s response, and the system classifies which frequency (and thus which “intent”) the user focused on.

Each frequency corresponds to a specific **patient request** (like asking for water or signaling pain).

| Frequency (Hz) | Patient Intention |
|----------------|-------------------|
| 6.66 Hz | Needs Water  |
| 7.50 Hz | Needs Food  |
| 8.57 Hz | In Pain  |
| 10.0 Hz | Needs Repositioning  |
| 12.0 Hz | Emergency / Needs Help  |


## System Architecture

### EEG Signal Acquisition (BCI)
EEG data is recorded from occipital channels (O1, O2) using an EEG device.

### Python Processing Unit
- Reads `.dat` EEG files (WFDB format).  
- Extracts **PSD (Power Spectral Density)** features using **Welch’s method**.  
- Classifies flicker frequency using a **Random Forest Machine Learning model**.  
- Sends the detected frequency via serial communication to **ESP32**.

### ESP32 IoT Controller
- Receives frequency commands from Python.  
- Activates the corresponding **LED** and **buzzer** for visual/audible feedback.  
- Sends an **SMS alert** via **Twilio API** to notify caregivers instantly.


## Machine Learning Pipeline

| Step | Description |
|------|--------------|
| **Data Input** | EEG signal in `.dat` format |
| **Filtering** | Bandpass filter applied (5–40 Hz) |
| **Feature Extraction** | Welch PSD for dominant frequency components |
| **Model** | Random Forest Classifier |
| **Output** | Detected frequency → Corresponding patient request |

Model trained using labeled EEG samples corresponding to flicker stimuli.


## Technologies Used

- **Python** — EEG signal processing, PSD computation, ML model  
- **scikit-learn** — Random Forest classifier  
- **wfdb** — EEG data loading  
- **ESP32** — IoT microcontroller for alerts  
- **Twilio API** — SMS notification service  
- **Matplotlib / SciPy** — Signal visualization and analysis  


## Future Enhancements

- Replace offline EEG files with **live EEG stream** using **Emotiv SDK** or **Lab Streaming Layer (LSL)**  
- Add **voice synthesis feedback** for patients (e.g., “Water requested”)  
- Integrate with **mobile app** for real-time caregiver monitoring  
- Move **model inference onto ESP32 or Edge TPU** for edge AI capability  


## Summary

The **SSVEP-Based Patient Assistance System** demonstrates how **BCI + IoT + AI** can empower paralyzed individuals with an independent, safe, and reliable communication channel.  
By decoding neural signals and linking them to physical-world alerts, this system represents a vital step toward **assistive neurotechnology for healthcare**.

