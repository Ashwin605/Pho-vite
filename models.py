from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=True) # Nullable for Google users
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    profile_pic = db.Column(db.String(500), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    invitations = db.relationship('Invitation', backref='author', lazy=True)

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    vibe = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # New enhanced features
    family_name = db.Column(db.String(200), nullable=True)  # Family name
    celebrant_name = db.Column(db.String(200), nullable=True)  # Name of person being celebrated
    event_date = db.Column(db.String(100), nullable=True)  # Event date
    event_time = db.Column(db.String(100), nullable=True)  # Event time
    event_venue = db.Column(db.String(300), nullable=True)  # Event venue
    event_message = db.Column(db.Text, nullable=True)  # Custom message
    gallery_photos = db.Column(db.Text, nullable=True)  # JSON array of photo URLs
    
    # Event-specific fields
    bride_name = db.Column(db.String(200), nullable=True)  # For weddings
    groom_name = db.Column(db.String(200), nullable=True)  # For weddings
    bride_photo = db.Column(db.Text, nullable=True)  # Base64 bride photo
    groom_photo = db.Column(db.Text, nullable=True)  # Base64 groom photo
    celebrant_photo = db.Column(db.Text, nullable=True)  # For birthdays/other events
    couple_names = db.Column(db.String(400), nullable=True)  # For anniversaries
    baby_name = db.Column(db.String(200), nullable=True)  # For baby showers
    baby_gender = db.Column(db.String(50), nullable=True)  # For baby showers
    company_name = db.Column(db.String(200), nullable=True)  # For corporate events
    location_name = db.Column(db.String(200), nullable=True)
    location_address = db.Column(db.String(500), nullable=True)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)
    voice_message_url = db.Column(db.String(500), nullable=True)
    share_link = db.Column(db.String(100), unique=True, nullable=True)  # Unique shareable link
    view_count = db.Column(db.Integer, default=0)  # Track views

    story = db.Column(db.Text, nullable=True)  # AI-generated story/memory
    rsvps = db.relationship('RSVP', backref='invitation', lazy=True)

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invitation_id = db.Column(db.Integer, db.ForeignKey('invitation.id'), nullable=False)
    guest_name = db.Column(db.String(150), nullable=False)
    guest_email = db.Column(db.String(150), nullable=True)
    guest_message = db.Column(db.Text, nullable=True)  # Personal message from guest
    selfie_url = db.Column(db.String(500), nullable=True)
    vibe_pass_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default='attending')  # attending, declined
    date_responded = db.Column(db.DateTime, default=datetime.utcnow)

class GuestPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invitation_id = db.Column(db.Integer, db.ForeignKey('invitation.id'), nullable=False)
    guest_name = db.Column(db.String(150), nullable=False)
    photo_url = db.Column(db.String(500), nullable=False)
    message = db.Column(db.Text, nullable=True)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)
