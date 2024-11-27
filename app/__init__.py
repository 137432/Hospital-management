import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, render_template
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import click
from dotenv import load_dotenv
load_dotenv() 
from werkzeug.security import generate_password_hash  # Import for password hashing

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)
        # App configuration settings (including mail settings)
    app.config.from_pyfile('config.py')
    

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail = Mail(app)

    # Set up logging
    setup_logging(app)

    # Import and register the main blueprint
    from app.route import main_bp  # Ensure this points to the correct file
    app.register_blueprint(main_bp)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User  # Moved import here to avoid circular import
        return User.query.get(int(user_id))

    # Define the index route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Add admin command
    @app.cli.command('add-admin')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    def add_admin(username, email, password):
        """Add an admin user to the system."""
        from app.models import User  # Moved import here as well
        
        if User.query.filter_by(username=username).first() is not None:
            click.echo(f'User {username} already exists.')
            return

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        new_admin = User(username=username, email=email, password=hashed_password, role='admin', is_provider=False)  # Changed to False
        db.session.add(new_admin)
        db.session.commit()
        click.echo(f'Admin {username} added successfully.')

    return app

def setup_logging(app):
    """Set up logging for the application."""
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # Set up a rotating file handler for logging
    file_handler = RotatingFileHandler('logs/healthcare_app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info('Healthcare Management System startup')
