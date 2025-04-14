import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE

# Load dataset
file_path = "/content/Final Data_csv.csv"  # Adjusted path for uploaded file
df_new = pd.read_csv(file_path)

# Load and preprocess data
df_new["Rainfall"] = (df_new["Rainfall"] > 0).astype(int)
df_new.drop(columns=["name", "datetime", "preciptype"], inplace=True)

# Split dataset into features and target variable
X = df_new.drop(columns=["Rainfall"])
y = df_new["Rainfall"]

# Handle missing values using mean imputation
imputer = SimpleImputer(strategy="mean")
X_imputed = imputer.fit_transform(X)

# Standardize numerical features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

# Handle class imbalance using SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_scaled, y)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Train optimized Logistic Regression model
model = LogisticRegression(C=1.0, max_iter=500)
model.fit(X_train, y_train)

# Predict on test set
y_pred = model.predict(X_test)

# Save model and scaler
joblib.dump(model, "logistic_regression_model.pkl")
joblib.dump(scaler, "scaler.pkl")
print("Model and Scaler saved successfully.")

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Optimized Logistic Regression Model Accuracy: {accuracy * 100:.2f}%")
