from mailbox import Message
from smtplib import SMTPException
from dotenv import load_dotenv
from flask import Flask, flash, render_template, redirect, url_for, session, request, jsonify
import re
from authlib.integrations.flask_client import OAuth
import os
import time
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from flask_cors import CORS
import SurveyForm

load_dotenv()       #load env file for every change

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://127.0.0.1:3000'])
app.secret_key = os.urandom(24)


app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_APP_PASSWORD"),
)

mail = Mail(app)

# Dummy user storage (email/phone -> password)
users = {
    'admin@gmail.com': 'password123',
    'admin2@gmail.com': 'password123',
    '+1234567890': 'password123'
}

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id="1045716424808-g5ckn3rgeuj0h628f2acbershk2p5vc9.apps.googleusercontent.com",
    client_secret="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",
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth?hl=en",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "openid email profile"},
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration"
)

def is_valid_email(value):
    """Check if the input is a valid email format."""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, value)

def is_valid_phone(value):
    """Check if the input is a valid phone number format (e.g., +1234567890)."""
    phone_regex = r"^\+?[0-9]{10,15}$"  # Allows optional '+' and 10-15 digits
    return re.match(phone_regex, value)

@app.route('/session_data')
def session_data():
    """Returns session data for testing"""
    if 'user' in session:
        return jsonify({"user": session['user']}), 200
    elif 'google_user' in session:
        return jsonify({"user": session['google_user']['email']}), 200
    return jsonify({"error": "No user logged in"}), 401


@app.route('/')
def home():
    """Home page that shows email/phone or Google user info."""
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    elif 'google_user' in session:
        return render_template('home.html', user=session['google_user']['name'])
    return redirect(url_for('login_page'))

@app.route('/login', methods=['POST'])
def login_page():
    """API endpoint for login that accepts both email and phone numbers."""
    error = None
    print(f"[DEBUG] Session before: failed_attempts={session.get('failed_attempts')}, lockout_time={session.get('lockout_time')}")
    if 'failed_attempts' not in session:
        session['failed_attempts'] = 0
    if 'lockout_time' not in session:
        session['lockout_time'] = None

    if session['lockout_time']:
        lockout_time = session['lockout_time']
        current_time = time.time()
        print(f"[DEBUG] Lockout check: current_time={current_time}, lockout_time={lockout_time}")
        # If lockout time has passed, reset the failed attempts and lockout time
        if current_time > lockout_time:
            print("[DEBUG] Lockout expired, resetting failed_attempts and lockout_time.")
            session['failed_attempts'] = 0
            session['lockout_time'] = None
        else:
            # If within the lockout period, show an error and return
            error = f"Too many failed attempts. Please try again in {int(lockout_time - current_time)} seconds."
            print(f"[DEBUG] User is locked out: {error}")
            return jsonify(error=error), 400
    
    user_input = request.form.get('user_input', '').strip()  # Can be email or phone
    password = request.form.get('password')
    print(f"[DEBUG] Received user_input='{user_input}', password={'*' * len(password) if password else None}")
    if not user_input and not password:
        error = "Email/Phone and Password are required."
    elif not user_input:
        error = "Email/Phone field is required."
    elif not password:
        error = "Password field is required."
    elif not (is_valid_email(user_input) or is_valid_phone(user_input)):
        error = "Invalid email or phone number format."
    elif user_input not in users:
        error = "Invalid credentials."
    elif users[user_input] != password:
        error = "Invalid credentials."
    
    if not error:
        print("[DEBUG] Login successful. Resetting failed_attempts and lockout_time.")
        session['user'] = user_input
        session['failed_attempts'] = 0  # Reset failed attempts on successful login
        session['lockout_time'] = None  # Reset lockout time
        print(f"[DEBUG] Session after success: failed_attempts={session['failed_attempts']}, lockout_time={session['lockout_time']}")
        return jsonify(success=True, redirect="/Home")

    # If there's an error, increment failed attempts counter
    session['failed_attempts'] += 1
    print(f"[DEBUG] Failed login. Incremented failed_attempts to {session['failed_attempts']}")

    # If 3 failed attempts, set lockout time (30 seconds lockout)
    if session['failed_attempts'] > 3:
        session['lockout_time'] = time.time() + 30  # Lockout for 30 seconds
        error = "Too many failed attempts. Please try again in 30 seconds."
        print(f"[DEBUG] Lockout triggered. lockout_time set to {session['lockout_time']}")

    print(f"[DEBUG] Returning error: {error}")
    print(f"[DEBUG] Session after error: failed_attempts={session['failed_attempts']}, lockout_time={session['lockout_time']}")
    return jsonify(error=error), 400

@app.route('/google/login')
def google_login():
    """Redirect user to Google OAuth login page."""
    return google.authorize_redirect(url_for('google_callback', _external=True), prompt="select_account")

@app.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback and store user info in session, then redirect to frontend."""
    token = google.authorize_access_token()
    user_info = google.get("userinfo").json()
    session['google_user'] = user_info
    print(f"[DEBUG] Google login successful for user: {user_info}")
    # Redirect to the frontend's /home page
    return redirect("http://127.0.0.1:3000/Home")

@app.route('/logout')
def logout():
    """Logout and clear session data."""
    session.clear()
    return jsonify({"success": True}), 200

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm.SurveyForm()

    if form.validate_on_submit():
        flash("Survey submitted successfully!", "success")
        return redirect(url_for('home'))

    return render_template('survey.html', form=form)

@app.route("/survey/send", methods=["POST"])
def send_survey():
    data = request.get_json(force=True)
    print(data)

    # Extract models tried and cons
    models_tried = data.get("models", [])
    model_cons = {}

    # Loop over the keys and their corresponding cons
    for key, value in data.items():
        if key.endswith("_cons"):
            model = key.rsplit("_cons", 1)[0].capitalize()  # Get the model name and capitalize it
            if value.strip():
                model_cons[model] = value.strip()

    cons_section = "\n".join([f"{model}: {reason}" for model, reason in model_cons.items()]) or "None provided"
    models_line = f"Models Tried: {', '.join(models_tried) if models_tried else 'None'}"
    
    # Build the email body with all relevant information
    body = "\n".join([
        f"Name: {data.get('name', '')}",
        f"Birth Date: {data.get('birth_date', '')}",
        f"Education Level: {data.get('education_level', '')}",
        f"City: {data.get('city', '')}",
        f"Gender: {data.get('gender', '')}",
        models_line,
        "Defects/Cons Per Model:",
        cons_section,
        f"Use Case: {data.get('use_case', '')}",
    ])

    # Create the email message
    msg = Message(
        subject="AI Survey Result",
        sender="test.hesap458@gmail.com",
        recipients=["test.hesap458@gmail.com"],
        body=body,
    )

    try:
        mail.send(msg)
        flash("Survey sent successfully!", "success")
        return jsonify(success=True, message="Mail sent"), 200
    except SMTPException as exc:
        flash(f"Error: {exc}", "error")
        return jsonify(success=False, message=f"Mail error: {exc}"), 500

# In-memory store for survey templates
SURVEY_TEMPLATES = {}

import json
from datetime import datetime

SURVEY_SAVE_PATH = "saved_surveys.json"

@app.route("/create-survey", methods=["GET", "POST"])
def create_survey():
    if request.method == "POST":
        try:
            survey_data = request.get_json()
            survey_data["created_at"] = datetime.now().isoformat()

            if os.path.exists(SURVEY_SAVE_PATH):
                with open(SURVEY_SAVE_PATH, "r") as f:
                    surveys = json.load(f)
            else:
                surveys = []

            surveys.append(survey_data)
            survey_id = len(surveys) - 1  # Use index as ID

            with open(SURVEY_SAVE_PATH, "w") as f:
                json.dump(surveys, f, indent=2)

            return jsonify(success=True, message="Survey saved!", id=survey_id), 200
        except Exception as e:
            return jsonify(success=False, message=str(e)), 500

    return render_template("create_survey.html")

@app.route("/survey/<int:survey_id>")
def view_survey(survey_id):
    if os.path.exists(SURVEY_SAVE_PATH):
        with open(SURVEY_SAVE_PATH, "r") as f:
            surveys = json.load(f)
    else:
        return "No surveys found.", 404

    if 0 <= survey_id < len(surveys):
        return render_template("render_survey.html", survey=surveys[survey_id])
    else:
        return "Survey not found.", 404


if __name__ == '__main__':
    app.run(debug=True)
