import os

SECRET_KEY = "hospital_management_system"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE = os.path.join(BASE_DIR, "hospital.db")

MODEL_PATH = os.path.join(BASE_DIR, "models", "diabetes_xgboost_model.pkl")

# Gemini
GEMINI_API_KEY = "AQ.Ab8RN6LkdXO15wZdoSwA9u9JkACBby6EPl2R2TojahnsetfVyw"
GEMINI_MODEL = "gemini-2.0-flash"