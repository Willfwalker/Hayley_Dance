import flask
import os
import json
from datetime import datetime
import uuid

app = flask.Flask(__name__)
# Use a fixed secret key for Vercel deployment
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'haley-reynolds-dance-website-secret')

# Set session lifetime to 30 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = 1800

# Password for admin access - can be set as environment variable
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'HR1234')

# File to store messages - for local development
MESSAGES_FILE = 'messages.json'

# Function to load messages from JSON file
def load_messages():
    # For Vercel deployment, we'll use a simple in-memory storage
    # In a real app, you'd use a database or storage service
    if os.environ.get('VERCEL'):
        # Return empty list when deployed (you'd connect to a database here)
        return []

    # Local development uses JSON file
    if os.path.exists(MESSAGES_FILE):
        try:
            with open(MESSAGES_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Return empty list if file is empty or invalid
            return []
    else:
        # Create the file if it doesn't exist
        with open(MESSAGES_FILE, 'w') as f:
            json.dump([], f)
        return []

# Function to save messages to JSON file
def save_messages(messages):
    # For Vercel deployment, we'd save to a database
    if os.environ.get('VERCEL'):
        # In a real app, you'd save to a database here
        return True

    # Local development uses JSON file
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=4)
    return True

@app.route('/', methods=['GET', 'POST'])
def home():
    success_message = None
    error_message = None

    if flask.request.method == 'POST':
        try:
            name = flask.request.form.get('name')
            email = flask.request.form.get('email')
            subject = flask.request.form.get('subject')
            message = flask.request.form.get('message')

            # Validate form data
            if not all([name, email, subject, message]):
                error_message = "Please fill out all fields."
            elif '@' not in email or '.' not in email:
                error_message = "Please enter a valid email address."
            else:
                # Load existing messages
                messages = load_messages()

                # Add new message
                messages.append({
                    'name': name,
                    'email': email,
                    'subject': subject,
                    'message': message,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                # Save updated messages
                save_messages(messages)

                success_message = "Your message has been sent successfully!"
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"

    return flask.render_template('home.html', success_message=success_message, error_message=error_message)

@app.route('/messages', methods=['GET', 'POST'])
def view_messages():
    error = None

    # Check if user is already authenticated via session
    if flask.session.get('authenticated'):
        # Load messages from JSON file
        messages = load_messages()
        return flask.render_template('messages.html', messages=messages)

    # Handle login form submission
    if flask.request.method == 'POST':
        password = flask.request.form.get('password')

        if password == ADMIN_PASSWORD:
            # Set session to authenticated
            flask.session['authenticated'] = True
            # Load messages from JSON file
            messages = load_messages()
            return flask.render_template('messages.html', messages=messages)
        else:
            error = 'Incorrect password. Please try again.'

    # Show login form
    return flask.render_template('login.html', error=error)

@app.route('/logout')
def logout():
    # Clear the session
    flask.session.pop('authenticated', None)
    return flask.redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
