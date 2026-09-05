# ==========================================
# IMPORT LIBRARIES
# ==========================================
import streamlit as st
import numpy as np
import joblib

# ==========================================
# LOAD MODEL
# ==========================================
model = joblib.load("diabetes_xgboost_model.pkl")

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Diabetes Prediction System", layout="centered")

st.title("🏥 Diabetes Prediction System")
st.write("Enter patient clinical details to check diabetes status")

st.markdown("---")

# ==========================================
# INPUT FIELDS
# ==========================================
pregnancies = st.number_input("Pregnancies", min_value=0, max_value=20, value=0)
glucose = st.number_input("Glucose Level", min_value=0.0, value=120.0)
blood_pressure = st.number_input("Blood Pressure", min_value=0.0, value=70.0)
skin_thickness = st.number_input("Skin Thickness", min_value=0.0, value=20.0)
insulin = st.number_input("Insulin Level", min_value=0.0, value=80.0)
bmi = st.number_input("BMI", min_value=0.0, value=25.0)
dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, value=0.5)
age = st.number_input("Age", min_value=1, max_value=120, value=30)

st.markdown("---")

# ==========================================
# PREDICTION
# ==========================================
if st.button("Predict Diabetes"):

    input_data = np.array([[pregnancies, glucose, blood_pressure,
                            skin_thickness, insulin, bmi,
                            dpf, age]])

    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    st.markdown("## 🩺 Prediction Result")

    if prediction == 1:
        st.error(f"⚠ Patient is Diabetic")
    else:
        st.success("✅ Patient is Not Diabetic")

    st.info(f"📊 Probability of Diabetes: {probability:.2f}")

    st.markdown("---")
    st.caption("Hospital Management System - Diabetes")