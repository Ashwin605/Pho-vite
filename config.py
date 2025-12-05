import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    # Google OAuth
    HARDCODED_CLIENT_ID = '413486107880-j063qhbqbpjuhmrsqjve8dceo3i7jrs9.apps.googleusercontent.com'
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', HARDCODED_CLIENT_ID).strip()
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
    
    # Jamendo
    JAMENDO_CLIENT_ID = os.getenv('JAMENDO_CLIENT_ID', 'cc68060f')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///vibecheck.db')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Admin
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'ashwinsrichandra2008@gmail.com').strip()
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'ashwin@2008').strip()
    
    # AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
