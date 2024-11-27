import click
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User

app = create_app()

@app.cli.command('add-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
def add_admin(username, email, password):
    """Add an admin user to the system."""
    
    # Check if the username already exists
    if User.query.filter_by(username=username).first() is not None:
        click.echo(f'User {username} already exists.')
        return

    # Hash the password before storing it
    hashed_password = generate_password_hash(password)

    # Create the new admin user
    new_admin = User(
        username=username,
        email=email,
        password_hash=hashed_password,  # Corrected to match the model attribute
        role='admin',  # Set role to 'admin'
        is_provider=False  # Set is_provider to False
    )

    # Add and commit the new user to the database
    db.session.add(new_admin)
    db.session.commit()
    click.echo(f'Admin {username} added successfully.')
