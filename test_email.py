from app import create_app
from services.email_service import EmailService
import logging
import time

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

def test_email():
    print("🚀 Initializing App Context...")
    app = create_app()
    
    with app.app_context():
        print("📧 Attempting to send test email...")
        
        # Test 1: Send a generic test email
        recipient = "ashwinsrichandra2008@gmail.com"  # Sending to yourself to verify
        subject = "Test Email from PhoVite System"
        body = """
        <h1>It Works! 🎉</h1>
        <p>This is a test email to verify that your PhoVite email configuration is correct.</p>
        <p>If you are reading this, the <strong>EmailService</strong> is successfully connecting to Gmail!</p>
        """
        
        success = EmailService.send_email(subject, recipient, body)
        
        if success:
            print(f"✅ Email thread started! Check your inbox ({recipient}) in a few seconds.")
        else:
            print("❌ Failed to initiate email send. Check configs.")

        # Allow some time for the background thread to execute before script exits
        print("⏳ Waiting for background thread...")
        time.sleep(5)
        print("Done.")

if __name__ == "__main__":
    test_email()
