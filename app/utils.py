from flask_mail import Message
from flask import current_app
from app import mail  # Assuming 'mail' is initialized in your app

def send_otp_email(recipient, otp):
    """Function to send OTP email to the recipient."""
    msg = Message("Your OTP Code", recipients=[recipient])
    msg.body = f"Your OTP code is {otp}"

    try:
        # Sending the email using the Flask-Mail extension
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
