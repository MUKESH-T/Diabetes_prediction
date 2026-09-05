from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash

from config import SECRET_KEY

from utils import db
from utils import auth
from utils import prediction
from utils import recommendation
from utils import chatbot


app = Flask(__name__)
app.secret_key = SECRET_KEY


# =====================================================
# DATABASE TABLES
# =====================================================

def create_tables():

    db.execute_query("""

    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        phone TEXT,

        age INTEGER,

        gender TEXT,

        password TEXT NOT NULL

    )

    """)

    db.execute_query("""

    CREATE TABLE IF NOT EXISTS predictions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER,

        pregnancies REAL,

        glucose REAL,

        blood_pressure REAL,

        skin_thickness REAL,

        insulin REAL,

        bmi REAL,

        dpf REAL,

        age REAL,

        prediction INTEGER,

        probability REAL,

        recommendation TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)


create_tables()


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template("index.html")


# =====================================================
# REGISTER
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        phone = request.form["phone"]

        age = request.form["age"]

        gender = request.form["gender"]

        password = request.form["password"]

        auth.register_user(
    name,
    email,
    phone,
    age,
    gender,
    password
)   

        db.execute_query(
            """
            UPDATE users
            SET phone=?,
                age=?,
                gender=?
            WHERE email=?
            """,
            (phone, age, gender, email)
        )

        flash("Registration Successful")

        return redirect(url_for("login"))

    return render_template("register.html")


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        user = auth.login_user(email, password)

        if user:

            session["user_id"] = user["id"]

            session["name"] = user["name"]

            session["email"] = user["email"]

            return redirect(url_for("dashboard"))

        flash("Invalid Email or Password")

    return render_template("login.html")


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))

# =====================================================
# DASHBOARD
# =====================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    records = db.execute_query(
        """
        SELECT COUNT(*) AS total
        FROM predictions
        WHERE user_id=?
        """,
        (session["user_id"],),
        True
    )

    total_predictions = records[0]["total"]

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions
    )


# =====================================================
# PROFILE
# =====================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.execute_query(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (session["user_id"],),
        True
    )[0]

    return render_template(
        "profile.html",
        user=user
    )


# =====================================================
# PREDICTION PAGE
# =====================================================

@app.route("/prediction")
def prediction_page():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("prediction.html")


# =====================================================
# PREDICT
# =====================================================

@app.route("/predict", methods=["POST"])
def predict():

    if "user_id" not in session:
        return redirect(url_for("login"))

    pregnancies = float(request.form["pregnancies"])
    glucose = float(request.form["glucose"])
    blood_pressure = float(request.form["blood_pressure"])
    skin_thickness = float(request.form["skin_thickness"])
    insulin = float(request.form["insulin"])
    bmi = float(request.form["bmi"])
    dpf = float(request.form["dpf"])
    age = float(request.form["age"])

    features = [
        pregnancies,
        glucose,
        blood_pressure,
        skin_thickness,
        insulin,
        bmi,
        dpf,
        age
    ]

    pred, prob = prediction.predict(features)

    patient = {
        "pregnancies": pregnancies,
        "glucose": glucose,
        "blood_pressure": blood_pressure,
        "skin_thickness": skin_thickness,
        "insulin": insulin,
        "bmi": bmi,
        "dpf": dpf,
        "age": age
    }

    ai_recommendation = recommendation.get_recommendation(
        patient,
        pred,
        prob
    )

    db.execute_query(
        """
        INSERT INTO predictions(
            user_id,
            pregnancies,
            glucose,
            blood_pressure,
            skin_thickness,
            insulin,
            bmi,
            dpf,
            age,
            prediction,
            probability,
            recommendation
        )
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            session["user_id"],
            pregnancies,
            glucose,
            blood_pressure,
            skin_thickness,
            insulin,
            bmi,
            dpf,
            age,
            pred,
            prob,
            ai_recommendation
        )
    )

    return render_template(
        "result.html",
        prediction=pred,
        probability=round(prob * 100, 2),
        recommendation=ai_recommendation
    )


# =====================================================
# HISTORY
# =====================================================

@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("login"))

    history = db.execute_query(
        """
        SELECT *
        FROM predictions
        WHERE user_id=?
        ORDER BY created_at DESC
        """,
        (session["user_id"],),
        True
    )

    return render_template(
        "history.html",
        history=history
    )
# =====================================================
# GEMINI AI CHATBOT
# =====================================================

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot_page():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        question = request.form["question"]

        answer = chatbot.ask_chatbot(question)

        return render_template(
            "chatbot_page.html",
            question=question,
            answer=answer
        )

    return render_template("chatbot_page.html")


# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(404)
def page_not_found(error):

    return "<h2>404 - Page Not Found</h2>", 404


@app.errorhandler(500)
def internal_server_error(error):

    return "<h2>500 - Internal Server Error</h2>", 500


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )