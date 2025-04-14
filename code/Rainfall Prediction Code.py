import serial
import json
import joblib
import numpy as np

# Load scaler and model
scaler = joblib.load('scaler.pkl')
model = joblib.load('logistic_regression_model.pkl')

# Setup serial communication
port = 'COM5'  # Replace with your ESP32 port
baud_rate = 115200
ser = serial.Serial(port, baud_rate, timeout=2)

def preprocess_data(sensor_data):
    features = np.array([
        sensor_data['temp'], sensor_data['humidity'], sensor_data['pressure'],
        sensor_data['windspeed'], sensor_data['winddir'], sensor_data['dew'],
        sensor_data['cloudcover'], sensor_data['visibility']
    ]).reshape(1, -1)
    return scaler.transform(features)

def predict_rainfall(sensor_data):
    scaled_data = preprocess_data(sensor_data)
    prediction = model.predict(scaled_data)
    return prediction[0]

def main():
    print("Waiting for data from ESP32...")
    while True:
        try:
            if ser.in_waiting > 0:
                # Read and decode data
                esp32_data = ser.readline().decode('utf-8').strip()

                # Attempt to parse JSON
                sensor_data = json.loads(esp32_data)

                # Check if required keys exist
                required_keys = ['temp', 'humidity', 'pressure', 'windspeed', 'winddir', 'dew', 'cloudcover', 'visibility']
                if all(key in sensor_data for key in required_keys):
                    rainfall = predict_rainfall(sensor_data)

                    print(f"Predicted Rainfall: {rainfall} mm")

                    # Send 1 if rainfall ≥ 0.5 mm, else 0
                    result = 1 if rainfall >= 0.5 else 0
                    ser.write(f"{result}\n".encode())

                    # Wait for next LDR trigger event
                    print("Waiting for next LDR trigger...\n")

                    # Flush input to avoid duplicates
                    ser.flushInput()
                else:
                    print("Incomplete sensor data received. Skipping...")
        except json.JSONDecodeError:
            print("Invalid JSON received. Waiting for next valid input...\n")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
