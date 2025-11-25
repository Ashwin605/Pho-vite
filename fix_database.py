"""
Quick script to add is_admin column to the database
Run this if you get the "no such column: user.is_admin" error
"""
from app import app, db
from sqlalchemy import inspect, text

with app.app_context():
    try:
        inspector = inspect(db.engine)
        
        # Check if user table exists
        if 'user' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'is_admin' not in columns:
                print("Adding is_admin column to user table...")
                with db.engine.begin() as conn:
                    conn.execute(text('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL'))
                print("✅ is_admin column added successfully!")
            else:
                print("✅ is_admin column already exists!")
        else:
            print("User table doesn't exist yet. Run the app to create it.")
    except Exception as e:
        print(f"Error: {e}")

