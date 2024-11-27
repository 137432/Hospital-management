import os

class Config:
    """Base configuration class for Healthcare Management System."""

    # Secret key for session management and security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable event system to save memory

    # Flask-WTF settings
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True') == 'True'  # Enable CSRF protection

    # Flask-Login settings
    LOGIN_VIEW = 'auth.login'  # Redirect to this view if user needs to log in
    SESSION_PROTECTION = 'strong'  # Strong level of session security

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.mailtrap.io')  # Default to Mailtrap
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))  # Use the correct port, often 587 for TLS
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') in ['True', 'true', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        raise ValueError("MAIL_USERNAME and MAIL_PASSWORD must be set in the environment variables.")
    
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'no-reply@yourdomain.com')

    # Application settings
    APP_NAME = 'Healthcare Management System'
    DEBUG = os.environ.get('DEBUG', '0') == '1'
    TESTING = os.environ.get('TESTING', '0') == '1'

    # Logging settings
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'False').lower() in ['true', '1']

    # Security settings
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'your_salt_here')

    # Additional Features and Analytics settings
    ENABLE_ANALYTICS = os.environ.get('ENABLE_ANALYTICS', '0') == '1'
    ENABLE_LOGGING = os.environ.get('ENABLE_LOGGING', '1') == '1'

    # Additional mail configuration for debugging
    @classmethod
    def init_app(cls, app):
        """Initialize additional application settings."""
        if cls.LOG_TO_STDOUT:
            import logging
            from logging import StreamHandler
            handler = StreamHandler()
            handler.setLevel(logging.INFO)
            app.logger.addHandler(handler)
