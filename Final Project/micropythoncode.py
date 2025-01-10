from machine import Pin
import time

# GPIO setup
light_pin = machine.Pin(2, machine.Pin.OUT)

# Pre-trained model coefficients (example values; replace with your trained model's values)
# These coefficients correspond to a linear regression model for weather prediction
coefficients = {
    "maxtemp": 0.7,
    "mintemp": 0.5,
    "temp": 0.6,
    "humidity": 0.8,
    "rainfall": -0.3,
    "pressure": 0.4,
    "intercept": 10  # Adjust based on your model
}

# Predict weather metrics using a simple linear model
def predict_weather(day, month, year):
    # Dummy feature values (e.g., encoded date features or other features)
    # Replace this part with your actual feature extraction logic
    features = [day, month, year]
    
    # Example: Combine features linearly (replace with actual logic)
    maxtemp = coefficients["maxtemp"] * features[0] + coefficients["intercept"]
    mintemp = coefficients["mintemp"] * features[1] + coefficients["intercept"]
    temp = coefficients["temp"] * features[2] + coefficients["intercept"]
    humidity = coefficients["humidity"] * features[0] + coefficients["intercept"]
    rainfall = coefficients["rainfall"] * features[1] + coefficients["intercept"]
    pressure = coefficients["pressure"] * features[2] + coefficients["intercept"]

    return {
        "maxtemp": maxtemp,
        "mintemp": mintemp,
        "temp": temp,
        "humidity": humidity,
        "rainfall": rainfall,
        "pressure": pressure,
    }

# Control GPIO pin based on rainfall prediction
def control_light(rainfall):
    if rainfall < 2.5:
        light_pin.on()  # Turn on light
        print("Rainfall is low. Light turned ON.")
    else:
        light_pin.off()  # Turn off light
        print("Rainfall is sufficient. Light turned OFF.")

# Main function
def main():
    # Example user input
    day = int(input("Enter day: "))
    month = int(input("Enter month: "))
    year = int(input("Enter year: "))
    
    # Predict weather
    prediction = predict_weather(day, month, year)
    print("Weather Prediction:", prediction)
    
    # Control light based on rainfall
    control_light(prediction["rainfall"])

# Run the main function
if __name__ == "__main__":
    main()
