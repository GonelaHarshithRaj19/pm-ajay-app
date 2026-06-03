import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
data = pd.read_csv("data/projects.csv")

# Encode categorical columns
le_component = LabelEncoder()
le_state = LabelEncoder()
le_agency = LabelEncoder()
le_status = LabelEncoder()

data['Component'] = le_component.fit_transform(data['Component'])
data['State'] = le_state.fit_transform(data['State'])
data['Agency_Type'] = le_agency.fit_transform(data['Agency_Type'])
data['Status'] = le_status.fit_transform(data['Status'])

# Features and target
X = data[['Component','State','Agency_Type','Funds_Allocated','Funds_Utilized','Completion_Percentage','Delay_Days']]
y = data['Status']

# Train test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "model.pkl")

print("Model trained and saved successfully!")