import logging
from threading import Thread
from flask import current_app, render_template_string
from flask_mail import Message
from extensions import mail

class EmailService:
    """
    Scalable Email Service using asynchronous threading.
    This prevents the main application thread from blocking while waiting for 
    external SMTP servers or APIs.
    """

    @staticmethod
    def _send_async_email(app, msg):
        """
        Background task to send email with context
        """
        with app.app_context():
            try:
                mail.send(msg)
                logging.info(f"📧 Email sent successfully to {msg.recipients}")
            except Exception as e:
                logging.error(f"🔥 Failed to send email to {msg.recipients}: {str(e)}")

    @staticmethod
    def send_email(subject, recipients, html_body, sender=None):
        """
        Triggers the asynchronous email sending process.
        """
        app = current_app._get_current_object()
        
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            logging.warning("⚠️ Email configuration missing. Skipping email send.")
            logging.info(f"DUMMY EMAIL - To: {recipients} | Subject: {subject}")
            return False

        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_body,
            sender=sender or app.config.get('MAIL_DEFAULT_SENDER')
        )

        # Offload to a background thread for scalability
        thr = Thread(target=EmailService._send_async_email, args=(app, msg))
        thr.start()
        return True

    @staticmethod
    def send_rsvp_confirmation(guest_email, guest_name, event_name, share_link):
        """
        Sends a confirmation email to the guest with their Vibe Pass details.
        """
        subject = f"You're on the list! RSVP Confirmed for {event_name}"
        
        # In a real app, use render_template('email/rsvp_confirmation.html', ...)
        # For this setup, we'll use an inline template for simplicity/portability
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">You're In! 🎉</h1>
            </div>
            <div style="border: 1px solid #ddd; padding: 30px; border-radius: 0 0 10px 10px; background: #fff;">
                <p>Hi <strong>{guest_name}</strong>,</p>
                <p>Thanks for RSVPing ensuring you'll be there for <strong>{event_name}</strong>!</p>
                
                <div style="background: #f4f6f8; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                    <p style="margin: 0; font-size: 14px; color: #666;">View the event details anytime:</p>
                    <a href="{share_link}" style="display: inline-block; background: #764ba2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; margin-top: 10px; font-weight: bold;">View Invitation</a>
                </div>
                
                <p>We've let the host know you're coming.</p>
                <p>See you there!</p>
                <br>
                <p style="font-size: 12px; color: #999;">Sent with ❤️ by PhoVite</p>
            </div>
        </div>
        """
        
        return EmailService.send_email(subject, guest_email, html_body)

    @staticmethod
    def send_host_notification(host_email, guest_name, guest_message, event_name, status='attending'):
        """
        Notifies the host when someone RSVPs.
        """
        subject = f"New RSVP: {guest_name} is {status}!"
        
        status_color = "#22c55e" if status == 'attending' else "#ef4444"
        
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <div style="background: #1e1b4b; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h2 style="color: white; margin: 0;">New RSVP Alert 🔔</h2>
            </div>
            <div style="border: 1px solid #ddd; padding: 30px; border-radius: 0 0 8px 8px; background: #fff;">
                <p>You have a new response for <strong>{event_name}</strong>.</p>
                
                <div style="border-left: 4px solid {status_color}; padding-left: 15px; margin: 20px 0;">
                    <p style="font-size: 18px; font-weight: bold; margin: 0;">{guest_name}</p>
                    <p style="color: {status_color}; font-weight: bold; margin: 5px 0;">{status.upper()}</p>
                    <p style="font-style: italic; color: #555;">"{guest_message}"</p>
                </div>
                
                <a href="https://phovite-custom-link.com/dashboard" style="color: #667eea; text-decoration: none; font-size: 14px;">View all RSVPs in your dashboard &rarr;</a>
            </div>
        </div>
        """
        
        return EmailService.send_email(subject, host_email, html_body)
