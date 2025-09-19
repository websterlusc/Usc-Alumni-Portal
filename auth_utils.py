"""
Authentication and Email Utilities for USC IR Portal
Handles password generation, resets, and user notifications
"""

import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

def generate_random_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def generate_random_password(length=12):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def send_password_reset_email(user_email, user_name, new_password, reset_type="admin"):
    """Send password reset notification"""
    try:
        smtp_user = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')

        if not smtp_user or not smtp_password:
            print(f"Password reset email skipped - no SMTP config")
            return False

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = user_email
        msg['Subject'] = "USC IR Portal - Password Reset"

        if reset_type == "admin":
            body = f"""Dear {user_name},

Your USC Institutional Research Portal password has been reset by an administrator.

NEW LOGIN CREDENTIALS:
Email: {user_email}
Temporary Password: {new_password}

IMPORTANT SECURITY NOTICE:
1. This is a temporary password
2. Please log in immediately and change your password
3. Go to Profile > Change Password after logging in
4. Choose a strong, unique password

If you did not request this password reset, please contact ir@usc.edu.tt immediately.

Login at: [Your Portal URL]

USC Institutional Research Team"""

        elif reset_type == "forgot":
            body = f"""Dear {user_name},

You requested a password reset for your USC Institutional Research Portal account.

NEW LOGIN CREDENTIALS:
Email: {user_email}
New Password: {new_password}

SECURITY RECOMMENDATION:
Please log in and change this password immediately for security.
Go to Profile > Change Password after logging in.

If you did not request this reset, contact ir@usc.edu.tt immediately.

Login at: [Your Portal URL]

USC Institutional Research Team"""

        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(smtp_user, user_email, msg.as_string())
        server.quit()

        print(f"Password reset email sent to {user_email}")
        return True

    except Exception as e:
        print(f"Password reset email error: {str(e)}")
        return False


def send_account_creation_email(user_email, user_name, password, created_by="system"):
    """Send account creation notification"""
    try:
        smtp_user = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')

        if not smtp_user or not smtp_password:
            print(f"Account creation email skipped - no SMTP config")
            return False

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = user_email

        if created_by == "admin":
            msg['Subject'] = "USC IR Portal - Account Created"
            body = f"""Dear {user_name},

An administrator has created a USC Institutional Research Portal account for you.

YOUR LOGIN CREDENTIALS:
Email: {user_email}
Temporary Password: {password}

IMMEDIATE ACTION REQUIRED:
1. Log in using the credentials above
2. CHANGE YOUR PASSWORD immediately after logging in
3. Go to Profile > Change Password
4. Choose a strong, unique password that only you know

SECURITY NOTICE:
This temporary password was sent via email and should be changed immediately.
Never share your login credentials with anyone.

Login at: [Your Portal URL]

Welcome to the USC IR Portal!

USC Institutional Research Team"""

        else:  # Self registration
            msg['Subject'] = "USC IR Portal - Account Created"
            body = f"""Dear {user_name},

Welcome to the USC Institutional Research Portal!

Your account has been created successfully:
Email: {user_email}

Your account is currently pending admin approval. You will receive another email once approved and can begin using the portal.

If you have questions, contact ir@usc.edu.tt

USC Institutional Research Team"""

        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(smtp_user, user_email, msg.as_string())
        server.quit()

        print(f"Account creation email sent to {user_email}")
        return True

    except Exception as e:
        print(f"Account creation email error: {str(e)}")
        return False


def send_signup_confirmation_email(user_email, user_name):
    """Send confirmation email for new signups (pending approval)"""
    try:
        smtp_user = os.getenv('SMTP_USERNAME', '')
        smtp_password = os.getenv('SMTP_PASSWORD', '')

        if not smtp_user or not smtp_password:
            print(f"Signup confirmation email skipped - no SMTP config")
            return False

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = user_email
        msg['Subject'] = "USC IR Portal - Account Registration Received"

        body = f"""Dear {user_name},

Thank you for registering with the USC Institutional Research Portal.

REGISTRATION STATUS:
Your account has been created and is currently pending admin approval.

WHAT HAPPENS NEXT:
1. Our administrators will review your registration
2. You will receive another email once your account is approved
3. After approval, you can log in and access the portal features

APPROVAL TIME:
Account approvals are typically processed within 1-2 business days.

If you have questions about your registration, contact ir@usc.edu.tt

Thank you for your interest in the USC IR Portal.

USC Institutional Research Team
"""

        msg.attach(MIMEText(body, 'plain'))
        server.sendmail(smtp_user, user_email, msg.as_string())
        server.quit()

        print(f"Signup confirmation email sent to {user_email}")
        return True

    except Exception as e:
        print(f"Signup confirmation email error: {str(e)}")
        return False