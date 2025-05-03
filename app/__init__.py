# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Add your database URI here (e.g., for SQLite, MySQL, PostgreSQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'  # Example for SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    return app