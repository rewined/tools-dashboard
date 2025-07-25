#!/usr/bin/env python
"""Initialize the database with tables and default data."""

from app_toolkit import app, db, init_db

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    print(f"Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")