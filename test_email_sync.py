from app import create_app
from services.email_service import EmailService
import time

app = create_app()
with app.app_context():
    # Force sync send for testing mechanism
    try:
        from flask_mail import Message
        from extensions import mail
        msg = Message("PhoVite Test", recipients=["ashwinsrichandra2008@gmail.com"], body="Test")
        mail.send(msg)
        print("SENT_OK")
    except Exception as e:
        print(f"SENT_FAIL: {e}")
