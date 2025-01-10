import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib

# Load the dataset
data = pd.read_csv("D:\Final Project\code\new data 1.csv")

# Clean the dataset
data = data.drop(columns=['Unnamed: 8'])  # Remove unnecessary column
data['datetime'] = pd.to_datetime(data['datetime'])  # Convert to datetime
data['day_of_year'] = data['datetime'].dt.dayofyear  # Add day of the year as a feature

# Encode location name
label_encoder = LabelEncoder()
data['name_encoded'] = label_encoder.fit_transform(data['name'])

# Prepare features and target
X = data[['name_encoded', 'day_of_year']]
y = data[['tempmax', 'tempmin', 'temp', 'humidity', 'rainfall', 'pressure']]

# Split the dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model and encoder for MicroPython use
joblib.dump(model, "weather_model.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")

print("Model and encoder saved!")