import streamlit as st
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from prediction import predict
import joblib
import os


# Load the model without specifying compression
import pickle

# Load your trained model
with open('preprocessor.pkl' ,'rb') as file:
    loaded_preprocessor = pickle.load(file)
with open('dt_model.pkl', 'rb') as model_file:
    dt_model = pickle.load(model_file)
with open('poly.pkl', 'rb') as file:
    poly = pickle.load(file)


def preprocess_input_data(input_data):
    # Create interaction feature
    input_data['Pricing_Availability'] = input_data['PricingTier'] + '_' + input_data['ChargingStationAvailability']

    # Create polynomial features for 'DurationHours'
    poly_features = poly.transform(input_data[['DurationHours']])
    for i in range(poly_features.shape[1]):
        input_data[f'DurationHours_poly_{i}'] = poly_features[:, i]

    # Apply the preprocessor loaded from file
    input_data_processed = loaded_preprocessor.transform(input_data)
    return input_data_processed


# Function to recommend the best time to charge
def recommend_charging_time(prediction, start_hour):
    # Customize this logic based on your model's prediction and application context
    if prediction == 'High':
        return "late night or early morning"
    elif prediction == 'Medium':
        return "mid-morning or late evening"
    else:
        return f"around {start_hour} hours, as the grid load is expected to be low"

## Streamlit app
def main():
    st.title("EV Charging Station Load Predictor")

    # User inputs for each feature
    start_hour = st.slider("Select the Start Hour of Charging", 0, 23, 0)
    day_of_week = st.selectbox("Day of the Week", range(7))  # 0: Monday, 6: Sunday
    month = st.selectbox("Month", range(1, 13))  # 1: January, 12: December
    part_of_day = st.selectbox("Part of the Day", ["Morning", "Afternoon", "Evening", "Night"])
    user_charging_preference = st.selectbox("Charging Preference", ["Fast Charge", "Standard Charge"])
    pricing_tier = st.selectbox("Pricing Tier", ["Off-Peak", "Mid-Peak", "Peak"])
    charging_station_availability = st.selectbox("Charging Station Availability", ["Low", "Medium", "High"])
    duration_hours = st.slider("Estimated Charging Duration (Hours)", 0.5, 4.0, 1.0)

    # When the user clicks the 'Predict' button
    if st.button("Predict Grid Load Level and Best Time to Charge"):
        # Prepare the input data in the same format as your training data
        input_data = pd.DataFrame({
            'StartHour': [start_hour],
            'DayOfWeek': [day_of_week],
            'Month': [month],
            'PartOfDay': [part_of_day],
            'UserChargingPreference': [user_charging_preference],
            'PricingTier': [pricing_tier],
            'ChargingStationAvailability': [charging_station_availability],
            'DurationHours': [duration_hours]
        })

        # Preprocess the input data
        input_data_processed = preprocess_input_data(input_data)

        # Make a prediction
        prediction = dt_model.predict(input_data_processed)[0]

        # Display the prediction
        st.success(f"The predicted grid load level is: {prediction}")

        # Recommend the best time to charge
        best_time = recommend_charging_time(prediction, start_hour)
        st.info(f"The best time to charge is: {best_time}")

if __name__ == "__main__":
    main()
