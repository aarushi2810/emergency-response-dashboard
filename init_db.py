# init_db.py
from app import create_app, db  # Import your Flask app and db
from app.models import *  # Import all models to ensure they are registered with the database

# Create an instance of the app
app = create_app()

# Use the app's context to run db.create_all()
with app.app_context():
    db.create_all()  # Create the tables in the database