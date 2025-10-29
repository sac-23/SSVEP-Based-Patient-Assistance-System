# Requirements

<details>
<summary>Hardware Requirements</summary>

| Component                         | Quantity  | Description |
|----------------------------------|------------|--------------|
| EEG Headset (Emotiv / OpenBCI / any compatible device) | 1 | Used to capture SSVEP brain signals from the occipital region |
| ESP32 Dev Board                  | 1 | IoT controller for alerting and automation |
| LEDs (5 different colors or frequencies) | 5 | Flickering stimuli for SSVEP generation |
| Buzzer                           | 1 | Audio alert for caregiver notification |
| Jumper Wires                     | Multiple | For circuit connections |
| Breadboard                       | 1 | For prototype wiring |
| 5V Power Supply / USB Cable      | 1 | Power source for ESP32 and peripherals |

</details>

<details>
<summary>Software Requirements</summary>

- **Python 3.8+**  
- **Arduino IDE**  
- **ESP32 Board Package** installed in Arduino IDE  
- **Twilio Account** (for SMS API)  
- **Serial Communication** between Python and ESP32  

**Required Python Libraries:**
  - `numpy`  
  - `scipy`  
  - `matplotlib`  
  - `wfdb`  
  - `scikit-learn`  
  - `serial` (`pyserial` package)  
  - `requests` (for Twilio API)  

**Required Arduino Libraries:**
  - `WiFi.h`  
  - `HTTPClient.h`  
  - `ArduinoJson.h`  
  - `base64.h`

</details>

## Setup Notes
- Ensure correct **COM port** selection for serial communication between Python and ESP32.   
- For Twilio API, verify your phone number and store credentials securely (`SID`, `Auth Token`).  


