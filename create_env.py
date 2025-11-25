"""
Script to create .env file with admin credentials
Run this once to set up your admin login
"""
import os

env_content = """# Admin Credentials
ADMIN_EMAIL=admin@phovite.com
ADMIN_PASSWORD=admin123

# Flask Secret Key (for sessions)
SECRET_KEY=your-secret-key-change-this-to-random-string

# Database URL (SQLite by default)
DATABASE_URL=sqlite:///vibecheck.db

# Google OAuth (optional - for Google login)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Gemini API Key (for AI features)
GEMINI_API_KEY=
"""

if os.path.exists('.env'):
    print("[WARNING] .env file already exists!")
    response = input("Do you want to overwrite it? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        exit()

with open('.env', 'w') as f:
    f.write(env_content)

print("[SUCCESS] .env file created successfully!")
print("\nAdmin Login Credentials:")
print("  Email: admin@phovite.com")
print("  Password: admin123")
print("\n[WARNING] IMPORTANT: Change the password in .env file for security!")
print("\nNow restart your Flask app to use these credentials.")

