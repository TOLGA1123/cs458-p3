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
import SurveyForm

load_dotenv()       #load env file for every change

app = Flask(__name__)
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
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
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

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Login function that accepts both email and phone numbers."""
    error = None
    if 'failed_attempts' not in session:
        session['failed_attempts'] = 0
    if 'lockout_time' not in session:
        session['lockout_time'] = None

    if request.method == 'POST':
        if session['lockout_time']:
            lockout_time = session['lockout_time']
            current_time = time.time()

            # If lockout time has passed, reset the failed attempts and lockout time
            if current_time > lockout_time:
                session['failed_attempts'] = 0
                session['lockout_time'] = None
            else:
                # If within the lockout period, show an error and return
                error = f"Too many failed attempts. Please try again in {int(lockout_time - current_time)} seconds."
                return render_template('login.html', error=error)
            
        user_input = request.form.get('user_input', '').strip()  # Can be email or phone
        password = request.form.get('password')
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
            session['user'] = user_input
            session['failed_attempts'] = 0  # Reset failed attempts on successful login
            session['lockout_time'] = None  # Reset lockout time
            return redirect(url_for('home'))

        # If there's an error, increment failed attempts counter
        session['failed_attempts'] += 1

        # If 3 failed attempts, set lockout time (30 seconds lockout)
        if session['failed_attempts'] > 3:
            session['lockout_time'] = time.time() + 30  # Lockout for 30 seconds
            error = "Too many failed attempts. Please try again in 30 seconds."


    return render_template('login.html', error=error)

@app.route('/google/login')
def google_login():
    """Redirect user to Google OAuth login page."""
    return google.authorize_redirect(url_for('google_callback', _external=True), prompt="select_account")

@app.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback and store user info in session."""
    token = google.authorize_access_token()
    user_info = google.get("userinfo").json()
    session['google_user'] = user_info
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    """Logout and clear session data."""
    session.clear()
    return redirect(url_for('login_page'))

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

    model_cons = data.get("model_cons", {})
    cons_section = "\n".join([f"{model}: {reason}" for model, reason in model_cons.items()])

    body = "\n".join(
        [
            f"Name: {data.get('name', '')}",
            f"Birth Date: {data.get('birth_date', '')}",
            f"Education Level: {data.get('education_level', '')}",
            f"City: {data.get('city', '')}",
            f"Gender: {data.get('gender', '')}",
            f"Models Tried: {', '.join(data.get('models_tried', []))}",
            "Defects/Cons Per Model:",
            cons_section,
            f"Use Case: {data.get('use_case', '')}",
        ]
    )

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

if __name__ == '__main__':
    app.run(debug=True)
