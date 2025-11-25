import os
import json
import logging
import time
import requests
import base64
from io import BytesIO
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for, flash, abort
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
import secrets
import tempfile
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip
import requests
import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import textwrap

# Load environment variables
load_dotenv()

# Allow OAuth over HTTP for local testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# Configuration
# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# HARDCODED FALLBACKS (Ensures it works on hosted sites even if env vars aren't set)
HARDCODED_CLIENT_ID = '1045996945878-mod025k39cevdbiucbrfr2b2fdapgfdd.apps.googleusercontent.com'
HARDCODED_CLIENT_SECRET = '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'

app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID', HARDCODED_CLIENT_ID).strip()
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET', HARDCODED_CLIENT_SECRET).strip()

if not app.config['GOOGLE_CLIENT_ID'] or "your_google_client_id" in app.config['GOOGLE_CLIENT_ID']:
    logging.error("❌ GOOGLE_CLIENT_ID is not set or is still the default placeholder!")
    logging.error("👉 Please update your .env file with your actual Google Cloud credentials.")

# OAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={'scope': 'openid email profile'},
)

# Database Configuration
database_url = os.getenv('DATABASE_URL', 'sqlite:///vibecheck.db')
# Fix for Render's Postgres URL (SQLAlchemy requires postgresql://)
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---
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

# Create DB
with app.app_context():
    db.create_all()
    
    # Migration: Add is_admin column if it doesn't exist
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # Check if user table exists and if is_admin column exists
        if 'user' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'is_admin' not in columns:
                logging.info("Adding is_admin column to user table...")
                # Use raw SQL execution for SQLite compatibility
                with db.engine.begin() as conn:
                    conn.execute(db.text('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL'))
                logging.info("✅ is_admin column added successfully")
    except Exception as e:
        # If table doesn't exist or column already exists, that's fine
        if 'duplicate column' not in str(e).lower() and 'no such table' not in str(e).lower():
            logging.warning(f"Migration check: {e}")
        pass

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ADMIN AUTHENTICATION ---
# Admin credentials (can be overridden by environment variables)
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'ashwinsrichandra2008@gmail.com').strip()
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'ashwin@2008').strip()

# Log admin config status (without exposing password)
if ADMIN_EMAIL and ADMIN_PASSWORD:
    logging.info(f"✅ Admin credentials configured for: {ADMIN_EMAIL}")
else:
    logging.warning("⚠️ Admin credentials not configured. Set ADMIN_EMAIL and ADMIN_PASSWORD in .env file")

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        # Check if user is admin
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# --- AI CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    logging.error("⚠️ GEMINI_API_KEY not found or not configured in .env file!")
    logging.error("Please get your API key from: https://makersuite.google.com/app/apikey")
else:
    logging.info(f"✅ Gemini API key loaded (starts with: {GEMINI_API_KEY[:10]}...)")

# Image generation uses Pollinations.AI - NO API KEY NEEDED!
logging.info("✅ Image generation: Using Pollinations.AI (FREE, no auth required)")

genai.configure(api_key=GEMINI_API_KEY)

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/help')
def help_center():
    return render_template('help.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Auth Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        logging.info(f"Login attempt for email: {email}")
        
        # Check if this is an admin login (check plain password first)
        if ADMIN_EMAIL and ADMIN_PASSWORD:
            email_match = email.lower() == ADMIN_EMAIL.lower()
            password_match = password == ADMIN_PASSWORD
            
            logging.info(f"Admin check - Email match: {email_match}, Password match: {password_match}")
            
            if email_match and password_match:
                # Find or create admin user
                user = User.query.filter_by(email=ADMIN_EMAIL).first()
                if not user:
                    # Create admin user if doesn't exist
                    user = User(
                        email=ADMIN_EMAIL,
                        name='Admin',
                        password=generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256'),
                        is_admin=True
                    )
                    db.session.add(user)
                    db.session.commit()
                    logging.info(f"Created new admin user: {ADMIN_EMAIL}")
                else:
                    # Update existing user to be admin
                    user.is_admin = True
                    # Always update password to match current admin password
                    user.password = generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256')
                    db.session.commit()
                    logging.info(f"Updated user to admin: {ADMIN_EMAIL}")
                
                login_user(user)
                logging.info(f"Admin login successful: {email}")
                return redirect(url_for('admin_dashboard'))
        
        # Regular user login
        user = User.query.filter_by(email=email).first()
        if user and user.password and check_password_hash(user.password, password):
            login_user(user)
            # Redirect to admin dashboard if user is admin, otherwise regular dashboard
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            logging.warning(f"Failed login attempt for: {email}")
            flash('Invalid email or password', 'error')
    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', 'error')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
    return render_template('auth/signup.html')


@app.route('/login/google')
def google_login():
    if not app.config['GOOGLE_CLIENT_ID'] or "your_google_client_id" in app.config['GOOGLE_CLIENT_ID']:
        flash('Google Login is not configured. Please set GOOGLE_CLIENT_ID in .env', 'error')
        return redirect(url_for('login'))
        
    google = oauth.create_client('google')
    redirect_uri = url_for('google_authorize', _external=True)
    logging.info(f"Initiating Google Login. Redirect URI: {redirect_uri}")
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/callback')
def google_authorize():
    try:
        # Manual Token Exchange to Debug/Fix invalid_client
        code = request.args.get('code')
        if not code:
            flash('No code received from Google', 'error')
            return redirect(url_for('login'))

        token_url = "https://oauth2.googleapis.com/token"
        # Determine the redirect URI used in the request
        # We must match exactly what was used to generate the authorize URL
        # Since we are on localhost, let's try to be smart or just use the request.base_url
        redirect_uri = url_for('google_authorize', _external=True)
        
        # Force http if running locally and behind a proxy that might report https
        if 'localhost' in redirect_uri or '127.0.0.1' in redirect_uri:
            redirect_uri = redirect_uri.replace('https://', 'http://')

        payload = {
            'code': code,
            'client_id': app.config['GOOGLE_CLIENT_ID'],
            'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        logging.info("--- MANUAL TOKEN EXCHANGE ---")
        logging.info(f"Sending token request to: {token_url}")
        logging.info(f"Payload Client ID: {payload['client_id']}")
        logging.info(f"Payload Redirect URI: {payload['redirect_uri']}")
        # Don't log the full secret, just the length/start
        logging.info(f"Payload Secret: {payload['client_secret'][:5]}...")

        resp = requests.post(token_url, data=payload)
        
        logging.info(f"Token Response Status: {resp.status_code}")
        logging.info(f"Token Response Body: {resp.text}")

        if resp.status_code != 200:
            error_data = resp.json()
            error_msg = error_data.get('error_description') or error_data.get('error') or 'Unknown error'
            flash(f'Google Login Failed (Token Exchange): {error_msg}', 'error')
            return redirect(url_for('login'))

        token_data = resp.json()
        access_token = token_data.get('access_token')
        
        # Get User Info
        user_info_resp = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_resp.status_code != 200:
            flash('Failed to fetch user info from Google', 'error')
            return redirect(url_for('login'))
            
        user_info = user_info_resp.json()
        
        if not user_info.get('email'):
            flash('Failed to get email from Google.', 'error')
            return redirect(url_for('login'))

        # Check if user exists
        user = User.query.filter_by(email=user_info['email']).first()
        
        if not user:
            # Create new user
            random_password = secrets.token_urlsafe(16)
            user = User(
                email=user_info['email'],
                name=user_info['name'],
                google_id=user_info['sub'], # 'sub' is the unique ID in OIDC
                profile_pic=user_info.get('picture'),
                password=generate_password_hash(random_password)
            )
            db.session.add(user)
            db.session.commit()
        else:
            # Update existing user info
            if not user.google_id:
                user.google_id = user_info['sub']
            if not user.profile_pic:
                user.profile_pic = user_info.get('picture')
            db.session.commit()
            
        login_user(user)
        # Redirect to admin dashboard if user is admin, otherwise regular dashboard
        if user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))

    except Exception as e:
        logging.error(f"Google Login Error: {str(e)}")
        flash(f'Google Login Failed: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Admin Routes - Redirect to regular login (single login page)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Redirect admin login to regular login page (single login for all users)"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    # Redirect to regular login page
    return redirect(url_for('login'))

@app.route('/admin/logout')
@admin_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('Logged out from admin panel', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard with comprehensive statistics"""
    try:
        # Basic counts
        total_users = User.query.count()
        total_invitations = Invitation.query.count()
        
        # Active invitations (view_count > 0 or created in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_invitations = Invitation.query.filter(
            (Invitation.view_count > 0) | (Invitation.date_created >= thirty_days_ago)
        ).count()
        
        # RSVP statistics
        total_rsvps = RSVP.query.count()
        attending_rsvps = RSVP.query.filter_by(status='attending').count()
        declined_rsvps = RSVP.query.filter_by(status='declined').count()
        
        # Event type breakdown
        event_types = db.session.query(
            Invitation.event_type,
            db.func.count(Invitation.id).label('count')
        ).group_by(Invitation.event_type).all()
        event_type_breakdown = {event_type: count for event_type, count in event_types}
        
        # Recent activity (last 10 invitations and last 10 users)
        recent_invitations = Invitation.query.order_by(Invitation.date_created.desc()).limit(10).all()
        recent_users = User.query.order_by(User.id.desc()).limit(10).all()
        
        # Popular invitations (top 10 by view_count)
        popular_invitations = Invitation.query.order_by(Invitation.view_count.desc()).limit(10).all()
        
        # User statistics - get all users with their invitation counts
        all_users = User.query.all()
        users_with_invitations = []
        for user in all_users:
            users_with_invitations.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'is_admin': user.is_admin,
                'invitation_count': len(user.invitations)
            })
        
        # Invitation statistics with creator info
        all_invitations = Invitation.query.order_by(Invitation.date_created.desc()).all()
        
        # Calculate total views
        total_views = db.session.query(db.func.sum(Invitation.view_count)).scalar() or 0
        
        # Guest photos count
        total_guest_photos = GuestPhoto.query.count()
        
        return render_template('admin/dashboard.html',
            total_users=total_users,
            total_invitations=total_invitations,
            active_invitations=active_invitations,
            total_rsvps=total_rsvps,
            attending_rsvps=attending_rsvps,
            declined_rsvps=declined_rsvps,
            event_type_breakdown=event_type_breakdown,
            recent_invitations=recent_invitations,
            recent_users=recent_users,
            popular_invitations=popular_invitations,
            users_with_invitations=users_with_invitations,
            all_invitations=all_invitations,
            total_views=total_views,
            total_guest_photos=total_guest_photos
        )
    except Exception as e:
        logging.error(f"Error loading admin dashboard: {str(e)}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html',
            total_users=0,
            total_invitations=0,
            active_invitations=0,
            total_rsvps=0,
            attending_rsvps=0,
            declined_rsvps=0,
            event_type_breakdown={},
            recent_invitations=[],
            recent_users=[],
            popular_invitations=[],
            users_with_invitations=[],
            all_invitations=[],
            total_views=0,
            total_guest_photos=0
        )

@app.route('/dashboard')
@login_required
def dashboard():
    user_invites = Invitation.query.filter_by(user_id=current_user.id).order_by(Invitation.date_created.desc()).all()
    return render_template('dashboard.html', invites=user_invites, user=current_user)

@app.route('/api/delete-invitation/<int:invite_id>', methods=['DELETE'])
@login_required
def delete_invitation(invite_id):
    """Delete an invitation"""
    try:
        invitation = Invitation.query.get(invite_id)
        
        if not invitation:
            return jsonify({"success": False, "error": "Invitation not found"}), 404
        
        if invitation.user_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Delete associated RSVPs first
        RSVP.query.filter_by(invitation_id=invite_id).delete()
        
        # Delete the invitation
        db.session.delete(invitation)
        db.session.commit()
        
        logging.info(f"Deleted invitation {invite_id} by user {current_user.id}")
        return jsonify({"success": True, "message": "Invitation deleted successfully"})
    
    except Exception as e:
        logging.error(f"Error deleting invitation: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/edit/<int:invite_id>')
@login_required
def edit_invitation(invite_id):
    """Edit invitation page"""
    invitation = Invitation.query.get(invite_id)
    
    if not invitation:
        flash('Invitation not found', 'error')
        return redirect(url_for('dashboard'))
    
    if invitation.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_invitation.html', invitation=invitation)

@app.route('/api/update-invitation/<int:invite_id>', methods=['PUT'])
@login_required
def update_invitation(invite_id):
    """Update invitation details"""
    try:
        invitation = Invitation.query.get(invite_id)
        
        if not invitation:
            return jsonify({"success": False, "error": "Invitation not found"}), 404
        
        if invitation.user_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        data = request.json
        
        # Update fields
        if 'title' in data:
            invitation.title = data['title']
        if 'body' in data:
            invitation.body = data['body']
        if 'event_type' in data:
            invitation.event_type = data['event_type']
        if 'vibe' in data:
            invitation.vibe = data['vibe']
        if 'location_name' in data:
            invitation.location_name = data['location_name']
        if 'location_address' in data:
            invitation.location_address = data['location_address']
        
        db.session.commit()
        
        logging.info(f"Updated invitation {invite_id} by user {current_user.id}")
        return jsonify({"success": True, "message": "Invitation updated successfully"})
    
    except Exception as e:
        logging.error(f"Error updating invitation: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/create')
@login_required
def create():
    return render_template('create.html')

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/refine-prompt', methods=['POST'])
@login_required
def refine_prompt():
    try:
        data = request.json
        event_type = data.get('eventType')
        vibe = data.get('vibe')
        details = data.get('details')
        family_name = data.get('familyName', '')
        celebrant_name = data.get('celebrantName', '')

        logging.info(f"Refining prompt for user {current_user.id}: {event_type}, {vibe}, {family_name}")

        system_prompt = """
        You are an expert creative director and event planner. 
        Your goal is to take user input about an event and generate:
        1. A HIGHLY DETAILED, artistic image generation prompt for creating an ELEGANT BORDER/FRAME DESIGN (NOT a full scene).
        2. A catchy, short title for the invitation card.
        3. A warm, inviting body text for the card (max 2 sentences).

        Return ONLY a JSON object with keys: "image_prompt", "card_title", "card_body".
        
        CRITICAL INSTRUCTIONS FOR image_prompt:
        - Generate a DECORATIVE BORDER or FRAME design, NOT a full background scene
        - The design should be elegant, ornate borders that frame content in the CENTER
        - Focus on: floral borders, geometric patterns, elegant corners, decorative frames
        - Include details about: border style, corner ornaments, edge decorations, pattern motifs
        - The CENTER should remain CLEAR/WHITE/LIGHT for text and photos
        - Border should be around the edges only
        - Specify colors, textures, and ornamental details for the frame/border elements
        """

        user_prompt = f"""
        Event Type: {event_type}
        Theme/Style: {vibe}
        Family Name: {family_name}
        Celebrant Name: {celebrant_name}
        Details: {details}

        Create a DECORATIVE BORDER/FRAME DESIGN prompt for an invitation card.
        
        IMPORTANT: Design an ELEGANT BORDER around the edges, NOT a full background scene.
        The center should remain clear/white for text and photos.
        
        Border Design Elements to include:
        - Ornate corner decorations (floral, geometric, or thematic elements)
        - Elegant edge patterns (vines, filigree, geometric borders, cultural motifs)
        - Decorative accents specific to the event theme
        - Color scheme and materials (gold foil, floral watercolor, geometric lines, etc.)
        - Border width and style (delicate thin lines, ornate thick borders, minimalist modern, etc.)
        - Symmetrical or asymmetrical composition
        - Keep the CENTER AREA CLEAR and light-colored for content
        
        Based on the specific theme '{vibe}' for a {event_type}:
        
        BIRTHDAY BORDER DESIGNS:
        - Neon Party: Geometric neon lines border in electric pink/purple/blue, glowing corners with starburst effects, modern sharp angles, metallic gradients, futuristic frame style
        - Balloon Fest: Playful balloon border along edges, confetti corner decorations, rainbow colored frame, cheerful party motifs, floating streamers as border elements
        - Confetti Pop: Golden confetti scattered around border edges, sparkle corner accents, celebratory frame with party elements, warm metallic tones
        - Cake Dreams: Whimsical dessert themed border, pastel pink and cream frosting-like decorative edges, sweet treat corner ornaments, soft watercolor style frame
        
        WEDDING BORDER DESIGNS:
        - Royal Elegance: Opulent gold baroque frame, ornate corner flourishes, crystal-like embellishments, regal filigree patterns, luxurious gilded border
        - Floral Romance: Delicate roses and peonies forming border, soft watercolor floral corners, romantic vine patterns along edges, dreamy pastel floral frame
        - Classic White: Minimalist elegant white and gold border, simple refined corners, clean lines, subtle pearl-like accents, sophisticated frame
        - Garden Dream: Enchanted botanical border, green leaf patterns, hanging fairy lights corner details, natural floral frame, organic flowing design
        
        PARTY BORDER DESIGNS:
        - Disco Lights: Retro geometric border with disco ball motifs in corners, colorful spotlight ray patterns, 70s inspired frame, mirror ball reflections
        - Beach Vibes: Tropical border with palm leaf corners, wave patterns along edges, sunset gradient frame, beach-themed decorative elements
        - Retro Funk: 80s geometric pattern border, neon color blocks, vintage angular design, bold nostalgic frame style
        - Glow Party: Neon paint splash border, UV light effect edges, glowing geometric corners, electric energy frame design
        
        CORPORATE BORDER DESIGNS:
        - Professional: Clean minimalist border, corporate blue/gray thin lines, modern geometric corners, sleek professional frame
        - Modern Tech: Futuristic digital border, holographic edge effects, tech-inspired corner elements, blue circuit-like patterns, cutting-edge frame
        - Luxury Gold: Premium gold accent border, marble texture corners, sophisticated frame design, high-end metallic elements
        - Minimal Clean: Ultra-minimalist border, simple geometric lines, elegant white space frame, contemporary clean design
        
        ANNIVERSARY BORDER DESIGNS:
        - Romantic Rose: Blooming rose border, romantic red and gold corners, elegant floral frame, intimate decorative elements
        - Golden Years: Vintage gold ornate border, classic decorative corners, nostalgic frame style, timeless elegant design
        - Champagne: Luxury celebration border with bubbles and golden accents, sophisticated corner embellishments, elegant frame
        - Starry Night: Celestial border with star patterns, twinkling corner elements, dreamy night sky inspired frame
        
        BABY SHOWER BORDER DESIGNS:
        - Baby Blue: Soft blue cloud-like border, cute teddy bear corners, gentle pastel frame, nursery themed decorations
        - Soft Pink: Delicate pink flower border, sweet corner embellishments, soft pastel frame, gentle baby girl theme
        - Pastel Rainbow: Soft rainbow colored border, whimsical cloud corners, dreamy multi-color frame, gender-neutral design
        - Teddy Bear: Adorable teddy bear themed border, warm brown tone corners, cozy frame with soft toy motifs
        
        Make the border design description VERY SPECIFIC with 40-50 words.
        Include exact colors, textures, patterns, and ornamental details.
        
        CRITICAL REQUIREMENTS:
        - Do NOT include any text, words, letters, or typography in the design
        - Focus on BORDERS and FRAMES around the edges
        - Keep the CENTER AREA CLEAR (white/cream/light colored) for photos and text
        - Design decorative elements around the EDGES and CORNERS only
        - Create a beautiful frame that enhances but doesn't overpower the content
        """

        # Use actual available models from your API key
        model_names = ['gemini-2.5-flash', 'gemini-2.5-pro-preview-03-25']
        response = None
        last_error = None
        
        for model_name in model_names:
            try:
                logging.info(f"Trying Gemini model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(system_prompt + "\n\n" + user_prompt)
                if response:
                    logging.info(f"Successfully used model: {model_name}")
                    break
            except Exception as e:
                last_error = str(e)
                logging.warning(f"Model {model_name} failed: {last_error}")
                continue
        
        if not response:
            error_msg = "Unable to generate invitation content. "
            
            # Provide specific guidance based on the error
            if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
                error_msg += "Please configure your GEMINI_API_KEY in the .env file. Get your free API key from https://makersuite.google.com/app/apikey"
            elif last_error and ("API_KEY_INVALID" in last_error or "invalid" in last_error.lower()):
                error_msg += "Your API key appears to be invalid. Please check your GEMINI_API_KEY in the .env file."
            elif last_error and ("quota" in last_error.lower() or "limit" in last_error.lower()):
                error_msg += "API quota exceeded. Please check your usage at https://aistudio.google.com/app/apikey or try again later."
            else:
                error_msg += f"Technical details: {last_error}"
            
            logging.error(error_msg)
            raise Exception(error_msg)

        text_response = response.text.strip()
        # Clean up markdown if present
        if text_response.startswith("```json"):
            text_response = text_response[7:-3]
        
        result_json = json.loads(text_response)
        return jsonify({"success": True, "data": result_json})

    except Exception as e:
        logging.error(f"Error in refine-prompt: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-image', methods=['POST'])
@login_required
def generate_image():
    try:
        data = request.json
        image_prompt = data.get('image_prompt')
        user_photo_url = data.get('user_photo_url')
        family_name = data.get('familyName', '')
        celebrant_name = data.get('celebrantName', '')
        event_date = data.get('eventDate', '')
        event_time = data.get('eventTime', '')
        event_venue = data.get('eventVenue', '')
        event_message = data.get('eventMessage', '')
        event_type = data.get('eventType', 'General')
        
        # Event-specific data
        bride_name = data.get('brideName', '')
        groom_name = data.get('groomName', '')
        bride_photo = data.get('bridePhoto', '')
        groom_photo = data.get('groomPhoto', '')
        celebrant_photo = data.get('celebrantPhoto', '')
        couple_names = data.get('coupleNames', '')
        couple_photo = data.get('couplePhoto', '')
        baby_name = data.get('babyName', '')
        baby_gender = data.get('babyGender', '')
        company_name = data.get('companyName', '')
        
        logging.info(f"Generating image for user {current_user.id}. Event: {event_type}, Family: {family_name}, Celebrant: {celebrant_name}")

        output_url = ""

        # Use Pollinations.AI (100% FREE, NO API KEY NEEDED!)
        logging.info("Generating image with Pollinations.AI (FREE, no auth required)...")
        
        # Enhance the prompt for better quality
        enhanced_prompt = f"{image_prompt}, highly detailed, professional quality, vibrant colors, masterpiece, 8k"
        
        try:
            # Pollinations.AI - Simple URL-based API
            # Just encode the prompt in the URL - no authentication needed!
            import urllib.parse
            encoded_prompt = urllib.parse.quote(enhanced_prompt)
            
            # Pollinations.AI endpoint with parameters
            pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true&enhance=true"
            
            logging.info(f"Generating image with prompt: {enhanced_prompt[:100]}...")
            logging.info(f"Pollinations URL: {pollinations_url[:150]}...")
            
            # Download the image
            response = requests.get(pollinations_url, timeout=60)
            
            if response.status_code == 200:
                # Convert to base64 for display
                image_bytes = response.content
                
                # COMPOSITE PHOTOS BASED ON EVENT TYPE
                try:
                    # Open background image
                    bg_img = Image.open(BytesIO(image_bytes)).convert("RGBA")
                    draw = ImageDraw.Draw(bg_img)
                    
                    # Add Family Name at Top (for all events)
                    if family_name:
                        try:
                            try:
                                font_family = ImageFont.truetype("arial.ttf", 60)
                            except:
                                font_family = ImageFont.load_default()
                            
                            bbox = draw.textbbox((0, 0), family_name, font=font_family)
                            text_width = bbox[2] - bbox[0]
                            x = (bg_img.width - text_width) // 2
                            y = 30
                            
                            # Draw text with outline
                            for adj_x in range(-3, 4):
                                for adj_y in range(-3, 4):
                                    draw.text((x + adj_x, y + adj_y), family_name, font=font_family, fill='black')
                            draw.text((x, y), family_name, font=font_family, fill='#c084fc')
                            logging.info(f"✅ Family name '{family_name}' added")
                        except Exception as e:
                            logging.error(f"Failed to add family name: {e}")
                    
                    # EVENT-SPECIFIC PHOTO COMPOSITING
                    if event_type == 'Wedding' and bride_photo and groom_photo:
                        # WEDDING: Bride (left) + Heart + Groom (right)
                        try:
                            photo_size = (180, 180)
                            y_position = 120 if family_name else 60
                            
                            # Process Bride Photo (Left)
                            bride_img_data = bride_photo.split(',')[1] if ',' in bride_photo else bride_photo
                            bride_img = Image.open(BytesIO(base64.b64decode(bride_img_data))).convert("RGBA")
                            bride_img = bride_img.resize(photo_size, Image.Resampling.LANCZOS)
                            
                            # Create circular mask for bride
                            mask = Image.new('L', photo_size, 0)
                            mask_draw = ImageDraw.Draw(mask)
                            mask_draw.ellipse((0, 0) + photo_size, fill=255)
                            
                            bride_circle = Image.new('RGBA', photo_size, (0, 0, 0, 0))
                            bride_circle.paste(bride_img, (0, 0), mask)
                            
                            # Add pink border for bride
                            border_draw = ImageDraw.Draw(bride_circle)
                            border_draw.ellipse((0, 0, photo_size[0]-1, photo_size[1]-1), outline="#ec4899", width=5)
                            
                            # Process Groom Photo (Right)
                            groom_img_data = groom_photo.split(',')[1] if ',' in groom_photo else groom_photo
                            groom_img = Image.open(BytesIO(base64.b64decode(groom_img_data))).convert("RGBA")
                            groom_img = groom_img.resize(photo_size, Image.Resampling.LANCZOS)
                            
                            groom_circle = Image.new('RGBA', photo_size, (0, 0, 0, 0))
                            groom_circle.paste(groom_img, (0, 0), mask)
                            
                            # Add blue border for groom
                            border_draw = ImageDraw.Draw(groom_circle)
                            border_draw.ellipse((0, 0, photo_size[0]-1, photo_size[1]-1), outline="#3b82f6", width=5)
                            
                            # Calculate positions (side by side with gap)
                            gap = 80  # Gap for heart symbol
                            total_width = photo_size[0] * 2 + gap
                            bride_x = (bg_img.width - total_width) // 2
                            groom_x = bride_x + photo_size[0] + gap
                            
                            # Paste photos
                            bg_img.paste(bride_circle, (bride_x, y_position), bride_circle)
                            bg_img.paste(groom_circle, (groom_x, y_position), groom_circle)
                            
                            # Draw heart symbol in the middle
                            try:
                                heart_font = ImageFont.truetype("seguiemj.ttf", 60)  # Windows emoji font
                            except:
                                try:
                                    heart_font = ImageFont.truetype("arial.ttf", 60)
                                except:
                                    heart_font = ImageFont.load_default()
                            
                            heart_x = bride_x + photo_size[0] + (gap - 40) // 2
                            heart_y = y_position + (photo_size[1] - 60) // 2
                            
                            # Draw heart with glow effect
                            for offset in range(5, 0, -1):
                                alpha = 50 + (5 - offset) * 30
                                draw.text((heart_x - offset, heart_y), "❤️", font=heart_font, fill=(255, 100, 100, alpha))
                            draw.text((heart_x, heart_y), "❤️", font=heart_font, fill="#ff1744")
                            
                            logging.info("✅ Wedding photos composited with heart!")
                        except Exception as e:
                            logging.error(f"Wedding photo compositing failed: {e}")
                    
                    elif event_type == 'Birthday' and celebrant_photo:
                        # BIRTHDAY: Single centered photo
                        try:
                            photo_size = (200, 200)
                            y_position = 130 if family_name else 70
                            
                            photo_data = celebrant_photo.split(',')[1] if ',' in celebrant_photo else celebrant_photo
                            user_img = Image.open(BytesIO(base64.b64decode(photo_data))).convert("RGBA")
                            user_img = user_img.resize(photo_size, Image.Resampling.LANCZOS)
                            
                            # Create circular mask
                            mask = Image.new('L', photo_size, 0)
                            mask_draw = ImageDraw.Draw(mask)
                            mask_draw.ellipse((0, 0) + photo_size, fill=255)
                            
                            circle = Image.new('RGBA', photo_size, (0, 0, 0, 0))
                            circle.paste(user_img, (0, 0), mask)
                            
                            # Add colorful border
                            border_draw = ImageDraw.Draw(circle)
                            border_draw.ellipse((0, 0, photo_size[0]-1, photo_size[1]-1), outline="#c084fc", width=5)
                            
                            # Center position
                            x = (bg_img.width - photo_size[0]) // 2
                            bg_img.paste(circle, (x, y_position), circle)
                            
                            logging.info("✅ Birthday photo composited!")
                        except Exception as e:
                            logging.error(f"Birthday photo compositing failed: {e}")
                    
                    elif event_type == 'Anniversary' and couple_photo:
                        # ANNIVERSARY: Couple photo
                        try:
                            photo_size = (200, 200)
                            y_position = 130 if family_name else 70
                            
                            photo_data = couple_photo.split(',')[1] if ',' in couple_photo else couple_photo
                            user_img = Image.open(BytesIO(base64.b64decode(photo_data))).convert("RGBA")
                            user_img = user_img.resize(photo_size, Image.Resampling.LANCZOS)
                            
                            mask = Image.new('L', photo_size, 0)
                            mask_draw = ImageDraw.Draw(mask)
                            mask_draw.ellipse((0, 0) + photo_size, fill=255)
                            
                            circle = Image.new('RGBA', photo_size, (0, 0, 0, 0))
                            circle.paste(user_img, (0, 0), mask)
                            
                            # Gold border for anniversary
                            border_draw = ImageDraw.Draw(circle)
                            border_draw.ellipse((0, 0, photo_size[0]-1, photo_size[1]-1), outline="#fbbf24", width=5)
                            
                            x = (bg_img.width - photo_size[0]) // 2
                            bg_img.paste(circle, (x, y_position), circle)
                            
                            logging.info("✅ Anniversary photo composited!")
                        except Exception as e:
                            logging.error(f"Anniversary photo compositing failed: {e}")
                    
                    # Fallback to user_photo_url if provided
                    elif user_photo_url:
                        try:
                            photo_response = requests.get(user_photo_url, timeout=30)
                            if photo_response.status_code == 200:
                                user_img = Image.open(BytesIO(photo_response.content)).convert("RGBA")
                                photo_size = (200, 200)
                                user_img = user_img.resize(photo_size, Image.Resampling.LANCZOS)
                                
                                mask = Image.new('L', photo_size, 0)
                                mask_draw = ImageDraw.Draw(mask)
                                mask_draw.ellipse((0, 0) + photo_size, fill=255)
                                
                                output = Image.new('RGBA', photo_size, (0, 0, 0, 0))
                                output.paste(user_img, (0, 0), mask)
                                
                                border_draw = ImageDraw.Draw(output)
                                border_draw.ellipse((0, 0, photo_size[0]-1, photo_size[1]-1), outline="#c084fc", width=5)
                                
                                x = (bg_img.width - photo_size[0]) // 2
                                y = 120 if family_name else 50
                                bg_img.paste(output, (x, y), output)
                                
                                logging.info("✅ User photo composited!")
                        except Exception as e:
                            logging.error(f"User photo compositing failed: {e}")
                    
                    # Save back to bytes
                    buffer = BytesIO()
                    bg_img = bg_img.convert("RGB")
                    bg_img.save(buffer, format="JPEG", quality=95)
                    image_bytes = buffer.getvalue()
                    
                except Exception as comp_e:
                    logging.error(f"Image compositing failed: {comp_e}")
                    # Continue with original image if compositing fails

                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                output_url = f"data:image/jpeg;base64,{image_base64}"
                
                logging.info("✅ Image generated successfully with Pollinations.AI!")
            else:
                raise Exception(f"Pollinations.AI error: {response.status_code}")
                
        except Exception as e:
            logging.error(f"Pollinations.AI generation failed: {e}")
            # Fallback to a simpler model
            try:
                logging.info("Trying fallback: Pollinations.AI with simpler prompt...")
                simple_prompt = urllib.parse.quote(image_prompt)
                fallback_url = f"https://image.pollinations.ai/prompt/{simple_prompt}?width=1024&height=576&nologo=true"
                response = requests.get(fallback_url, timeout=60)
                if response.status_code == 200:
                    image_bytes = response.content
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    output_url = f"data:image/jpeg;base64,{image_base64}"
                    logging.info("✅ Image generated with fallback!")
                else:
                    raise Exception(f"Fallback also failed: {response.status_code}")
            except Exception as fallback_error:
                logging.error(f"All image generation attempts failed: {fallback_error}")
                raise Exception(f"Image generation failed. Please try again later.")
        
        # SAVE TO DB IF LOGGED IN
        if current_user.is_authenticated:
            try:
                import secrets
                import string
                
                title = f"{celebrant_name}'s {data.get('eventType', 'Event')}" if celebrant_name else data.get('title', 'Untitled Invitation')
                body = event_message if event_message else data.get('body', '')
                event_type = data.get('eventType', 'General')
                vibe = data.get('vibe', 'General')
                location_name = event_venue if event_venue else data.get('location_name', '')
                
                # Generate unique share link
                def generate_share_link():
                    chars = string.ascii_lowercase + string.digits
                    while True:
                        link = ''.join(secrets.choice(chars) for _ in range(8))
                        if not Invitation.query.filter_by(share_link=link).first():
                            return link

                new_invite = Invitation(
                    title=title,
                    body=body,
                    image_url=output_url,
                    event_type=event_type,
                    vibe=vibe,
                    user_id=current_user.id,
                    share_link=generate_share_link(),
                    family_name=family_name,
                    celebrant_name=celebrant_name,
                    event_date=event_date,
                    event_time=event_time,
                    event_venue=event_venue,
                    event_message=event_message,
                    location_name=location_name,
                    # Event-specific fields
                    bride_name=bride_name if bride_name else None,
                    groom_name=groom_name if groom_name else None,
                    bride_photo=bride_photo if bride_photo else None,
                    groom_photo=groom_photo if groom_photo else None,
                    celebrant_photo=celebrant_photo if celebrant_photo else None,
                    couple_names=couple_names if couple_names else None,
                    baby_name=baby_name if baby_name else None,
                    baby_gender=baby_gender if baby_gender else None,
                    company_name=company_name if company_name else None
                )
                db.session.add(new_invite)
                db.session.commit()
                logging.info(f"Saved invitation {new_invite.id} with share link: {new_invite.share_link}")
                
                return jsonify({
                    "success": True, 
                    "image_url": output_url,
                    "invitation_id": new_invite.id,
                    "share_link": new_invite.share_link
                })
            except Exception as db_e:
                logging.error(f"Failed to save to DB: {str(db_e)}")

        return jsonify({"success": True, "image_url": output_url})

    except Exception as e:
        logging.error(f"Error in generate-image: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# --- ENHANCED INVITATION ROUTES ---

@app.route('/invite/<share_link>')
def public_invitation(share_link):
    """Public invitation view - accessible to anyone - Clean view without header/footer"""
    invitation = Invitation.query.filter_by(share_link=share_link).first()
    
    if not invitation:
        return render_template('404.html'), 404
    
    # Increment view count
    invitation.view_count += 1
    db.session.commit()
    
    # Use the clean share template (no header/footer)
    return render_template('share_invitation.html', invitation=invitation)

@app.route('/api/enhance-invitation', methods=['POST'])
@login_required
def enhance_invitation():
    """Add gallery, location, and voice to invitation"""
    try:
        data = request.json
        invitation_id = data.get('invitation_id')
        
        invitation = Invitation.query.get(invitation_id)
        if not invitation or invitation.user_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Update gallery photos
        if 'gallery_photos' in data:
            invitation.gallery_photos = json.dumps(data['gallery_photos'])
        
        # Update location
        if 'location_name' in data:
            invitation.location_name = data['location_name']
            invitation.location_address = data.get('location_address')
            invitation.location_lat = data.get('location_lat')
            invitation.location_lng = data.get('location_lng')
        
        # Update voice message
        if 'voice_message_url' in data:
            invitation.voice_message_url = data['voice_message_url']
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "share_link": invitation.share_link,
            "share_url": f"{request.host_url}invite/{invitation.share_link}"
        })
    
    except Exception as e:
        logging.error(f"Error enhancing invitation: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/upload-voice', methods=['POST'])
@login_required
def upload_voice():
    """Upload voice message (15 seconds max)"""
    try:
        if 'voice' not in request.files:
            return jsonify({"success": False, "error": "No voice file"}), 400
        
        voice_file = request.files['voice']
        
        # Here you would upload to cloud storage (Uploadcare, S3, etc.)
        # For now, we'll return a placeholder
        # In production, integrate with Uploadcare or similar
        
        voice_url = "placeholder_voice_url"  # Replace with actual upload
        
        return jsonify({"success": True, "voice_url": voice_url})
    
    except Exception as e:
        logging.error(f"Error uploading voice: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate-video', methods=['POST'])
@login_required
def generate_video():
    """Generate a 10-15s hype video from invitation with optional music"""
    try:
        logging.info("🎬 Video generation started")
        
        data = request.json
        invitation_id = data.get('invitation_id')
        music_choice = data.get('music')  # Can be None or a music type
        duration = data.get('duration', 12)  # Default 12 seconds
        
        logging.info(f"Video request - ID: {invitation_id}, Music: {music_choice}, Duration: {duration}s")
        
        # Ensure duration is between 10-15 seconds
        duration = max(10, min(15, duration))
        
        invitation = Invitation.query.get(invitation_id)
        if not invitation:
            logging.error(f"Invitation {invitation_id} not found")
            return jsonify({"success": False, "error": "Invitation not found"}), 404
            
        if invitation.user_id != current_user.id:
            logging.error(f"Unauthorized access attempt for invitation {invitation_id}")
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        logging.info(f"Processing invitation: {invitation.title}")
            
        # 1. Download/Process Image
        logging.info("Step 1: Processing image...")
        if invitation.image_url.startswith('data:'):
            # Handle Base64 Image
            header, encoded = invitation.image_url.split(",", 1)
            img_data = base64.b64decode(encoded)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_img:
                tmp_img.write(img_data)
                img_path = tmp_img.name
            logging.info("Base64 image saved to temp file")
        else:
            # Handle Regular URL
            img_resp = requests.get(invitation.image_url)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_img:
                tmp_img.write(img_resp.content)
                img_path = tmp_img.name
            logging.info("URL image downloaded to temp file")
            
        # 2. Create Video Clip with specified duration
        logging.info(f"Step 2: Creating {duration}s video clip...")
        clip = ImageClip(img_path).set_duration(duration)
        logging.info("Image clip created successfully")
        
        # Add simple pan/zoom effect (Ken Burns)
        # Resize to be slightly larger to allow for movement
        w, h = clip.size
        clip = clip.resize(height=1920) # Vertical video target
        clip = clip.crop(x1=0, y1=0, width=1080, height=1920, x_center=clip.w/2, y_center=clip.h/2)
        
        # Create Text Clips (Reveal Effect)
        # We use a simple fade-in for the "reveal" effect
        
        # Create Text Clips (Reveal Effect) using PIL (Robust fallback)
        
        # Create Text Clips (Reveal Effect) using PIL (Robust fallback)
        
        def create_text_clip_pil(text, fontsize, color, max_width, duration, start_time, y_pos):
            clips = []
            try:
                # 1. Create PIL Image
                try:
                    # Try to use a font that matches the "Display" or "Serif" style of the invitation
                    # Times New Roman is a safe bet for a "classy" look matching the invitation style
                    # If you have specific font files (e.g. Playfair Display), you should load them here
                    font = ImageFont.truetype("times.ttf", fontsize) 
                except:
                    try:
                        font = ImageFont.truetype("arial.ttf", fontsize)
                    except:
                        font = ImageFont.load_default()
                
                # Wrap text
                avg_char_width = fontsize * 0.6
                chars_per_line = int(max_width / avg_char_width)
                lines = textwrap.wrap(text, width=chars_per_line)
                
                line_height = int(fontsize * 1.2)
                current_y = y_pos
                
                # Create a clip for EACH line to animate them separately
                for i, line in enumerate(lines):
                    # Create image for just this line
                    # Make it wide enough for the text
                    try:
                        bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), line, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1] + 20 # Add padding
                    except:
                        text_width = len(line) * avg_char_width
                        text_height = fontsize + 20

                    # Create image for this line
                    img = Image.new('RGBA', (max_width, int(text_height + 20)), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(img)
                    
                    x = (max_width - text_width) // 2
                    
                    # Draw outline/stroke
                    for adj in range(-3, 4):
                        for adj2 in range(-3, 4):
                            draw.text((x+adj, 10+adj2), line, font=font, fill='black')
                    draw.text((x, 10), line, font=font, fill=color)
                    
                    np_img = np.array(img)
                    
                    # Stagger start times: 0.5s delay per line
                    line_start = start_time + (i * 0.8) 
                    
                    txt_clip = ImageClip(np_img).set_duration(duration - (line_start - start_time)).set_start(line_start)
                    txt_clip = txt_clip.set_position(('center', current_y)).crossfadein(1.0)
                    clips.append(txt_clip)
                    
                    current_y += line_height
                
                return clips, current_y
                
            except Exception as e:
                logging.error(f"PIL Text generation failed: {e}")
                return [], y_pos

        clips_to_composite = [clip]

        # Title Text - MATCH INVITATION STYLE (Larger, Serif)
        # Invitation uses ~text-8xl which is very large
        title_clips, next_y = create_text_clip_pil(invitation.title, 120, 'white', 1000, 10, 0.5, 300)
        clips_to_composite.extend(title_clips)
        
        # Body Text - MATCH INVITATION STYLE
        # Invitation uses ~text-3xl
        body_start_time = 0.5 + (len(title_clips) * 0.5) + 0.5
        body_clips, next_y = create_text_clip_pil(invitation.body, 60, 'white', 900, 10, body_start_time, next_y + 60)
        clips_to_composite.extend(body_clips)

        # Location Text
        if invitation.location_name:
            location_start_time = body_start_time + (len(body_clips) * 0.5) + 0.5
            location_clips, _ = create_text_clip_pil(f"📍 {invitation.location_name}", 50, 'yellow', 900, 10, location_start_time, next_y + 40)
            clips_to_composite.extend(location_clips)
        
        logging.info("Step 3: Compositing clips...")
        final_clip = CompositeVideoClip(clips_to_composite)
        logging.info("Composite video created")

        # 4. Write to file
        # Save to static/videos so it can be served
        logging.info("Step 4: Writing video file...")
        video_dir = os.path.join(app.root_path, 'static', 'videos')
        os.makedirs(video_dir, exist_ok=True)
        
        filename = f"hype_{invitation.id}_{int(time.time())}.mp4"
        output_path = os.path.join(video_dir, filename)
        
        logging.info(f"Writing video to: {output_path}")
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio=False, logger=None)
        logging.info("✅ Video file written successfully!")
        
        # 5. Return URL
        video_url = url_for('static', filename=f'videos/{filename}', _external=True)
        logging.info(f"Video URL: {video_url}")
        
        # Clean up input image
        try:
            os.remove(img_path)
            logging.info("Temp image file cleaned up")
        except:
            pass
        
        return jsonify({"success": True, "video_url": video_url})

    except Exception as e:
        logging.error(f"❌ Error generating video: {str(e)}")
        logging.error(f"Full error: {repr(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/rsvp-submit', methods=['POST'])
def rsvp_submit():
    """Submit RSVP with guest data"""
    try:
        data = request.json
        invitation_id = data.get('invitation_id')
        guest_name = data.get('guest_name')
        guest_email = data.get('guest_email')
        guest_message = data.get('guest_message')
        
        if not invitation_id or not guest_name:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
            
        invitation = Invitation.query.get(invitation_id)
        if not invitation:
            return jsonify({"success": False, "error": "Invitation not found"}), 404
        
        # Create RSVP entry
        new_rsvp = RSVP(
            invitation_id=invitation_id,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_message=guest_message,
            status='attending'
        )
        
        db.session.add(new_rsvp)
        db.session.commit()
        
        logging.info(f"✅ RSVP received from {guest_name} for invitation {invitation_id}")
        
        # SEND EMAIL TO OWNER (Simulated for now)
        owner_email = User.query.get(invitation.user_id).email
        logging.info(f"📧 SENDING EMAIL TO OWNER: {owner_email}")
        logging.info(f"Subject: New RSVP from {guest_name}!")
        logging.info(f"Body: {guest_name} has RSVP'd to your event '{invitation.title}'.")
        
        # TODO: Integrate SendGrid/Mailgun here for actual emails
        
        return jsonify({
            "success": True, 
            "message": "RSVP received!",
            "rsvp_id": new_rsvp.id
        })
        
    except Exception as e:
        logging.error(f"RSVP error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/get-rsvps/<int:invitation_id>', methods=['GET'])
def get_rsvps(invitation_id):
    """Get all RSVPs for an invitation"""
    try:
        invitation = Invitation.query.get(invitation_id)
        if not invitation:
            return jsonify({"success": False, "error": "Invitation not found"}), 404
        
        rsvps = RSVP.query.filter_by(invitation_id=invitation_id).order_by(RSVP.date_responded.desc()).all()
        
        rsvps_data = [{
            'id': rsvp.id,
            'guest_name': rsvp.guest_name,
            'guest_email': rsvp.guest_email,
            'guest_message': rsvp.guest_message,
            'status': rsvp.status,
            'date_responded': rsvp.date_responded.strftime('%Y-%m-%d %H:%M:%S')
        } for rsvp in rsvps]
        
        return jsonify({
            "success": True,
            "rsvps": rsvps_data
        })
        
    except Exception as e:
        logging.error(f"Error fetching RSVPs: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/get-invitation-id-by-link/<share_link>', methods=['GET'])
@login_required
def get_invitation_id_by_link(share_link):
    """Get invitation ID from share link - for existing invitations"""
    try:
        invitation = Invitation.query.filter_by(share_link=share_link).first()
        
        if not invitation:
            return jsonify({"success": False, "error": "Invitation not found"}), 404
        
        if invitation.user_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        return jsonify({
            "success": True,
            "invitation_id": invitation.id
        })
        
    except Exception as e:
        logging.error(f"Error fetching invitation ID: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/guest-photo-upload', methods=['POST'])
def guest_photo_upload():
    """Upload guest photo OR wishes to invitation"""
    try:
        invitation_id = request.form.get('invitation_id')
        guest_name = request.form.get('guest_name')
        guest_message = request.form.get('guest_message', '')
        
        if not invitation_id or not guest_name:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        if not guest_message:
            return jsonify({"success": False, "error": "Please provide a message or wishes"}), 400
        
        # Photo is OPTIONAL - check if provided
        photo_url = None
        has_photo = False
        
        if 'guest_photo' in request.files:
            photo_file = request.files['guest_photo']
            
            # Check if file was actually selected
            if photo_file and photo_file.filename != '':
                # Convert photo to base64
                photo_bytes = photo_file.read()
                photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
                photo_url = f"data:image/jpeg;base64,{photo_base64}"
                has_photo = True
        
        # Save to database (photo_url can be None for text-only wishes)
        new_entry = GuestPhoto(
            invitation_id=invitation_id,
            guest_name=guest_name,
            photo_url=photo_url,
            message=guest_message
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        if has_photo:
            logging.info(f"Guest photo and message shared by {guest_name} for invitation {invitation_id}")
        else:
            logging.info(f"Guest wishes shared by {guest_name} for invitation {invitation_id}")
        
        return jsonify({
            "success": True,
            "message": "Shared successfully!",
            "photo_id": new_entry.id,
            "has_photo": has_photo
        })
        
    except Exception as e:
        logging.error(f"Error uploading guest content: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/guest-photos/<int:invitation_id>', methods=['GET'])
def get_guest_photos(invitation_id):
    """Get all guest photos for an invitation"""
    try:
        photos = GuestPhoto.query.filter_by(invitation_id=invitation_id).order_by(GuestPhoto.date_uploaded.desc()).all()
        
        photos_data = [{
            'id': photo.id,
            'guest_name': photo.guest_name,
            'photo_url': photo.photo_url,
            'message': photo.message,
            'date_uploaded': photo.date_uploaded.strftime('%Y-%m-%d %H:%M:%S')
        } for photo in photos]
        
        return jsonify({
            "success": True,
            "photos": photos_data
        })
        
    except Exception as e:
        logging.error(f"Error fetching guest photos: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# --- ADMIN API ROUTES ---

@app.route('/admin/api/stats', methods=['GET'])
@admin_required
def admin_api_stats():
    """Get real-time statistics for admin dashboard"""
    try:
        total_users = User.query.count()
        total_invitations = Invitation.query.count()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_invitations = Invitation.query.filter(
            (Invitation.view_count > 0) | (Invitation.date_created >= thirty_days_ago)
        ).count()
        total_rsvps = RSVP.query.count()
        attending_rsvps = RSVP.query.filter_by(status='attending').count()
        declined_rsvps = RSVP.query.filter_by(status='declined').count()
        total_views = db.session.query(db.func.sum(Invitation.view_count)).scalar() or 0
        
        return jsonify({
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_invitations": total_invitations,
                "active_invitations": active_invitations,
                "total_rsvps": total_rsvps,
                "attending_rsvps": attending_rsvps,
                "declined_rsvps": declined_rsvps,
                "total_views": total_views
            }
        })
    except Exception as e:
        logging.error(f"Error fetching admin stats: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/api/users', methods=['GET'])
@admin_required
def admin_api_users():
    """Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str)
        
        query = User.query
        
        if search:
            query = query.filter(
                (User.email.contains(search)) | 
                (User.name.contains(search))
            )
        
        users = query.order_by(User.id.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = [{
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'is_admin': user.is_admin,
            'invitation_count': len(user.invitations),
            'date_created': user.id  # Using ID as proxy for creation order
        } for user in users.items]
        
        return jsonify({
            "success": True,
            "users": users_data,
            "total": users.total,
            "page": page,
            "per_page": per_page,
            "pages": users.pages
        })
    except Exception as e:
        logging.error(f"Error fetching users: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/api/users/<int:user_id>/delete', methods=['DELETE'])
@admin_required
def admin_api_delete_user(user_id):
    """Delete a user and all their invitations"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            return jsonify({"success": False, "error": "Cannot delete your own account"}), 400
        
        # Delete user's invitations first (cascade)
        invitations = Invitation.query.filter_by(user_id=user_id).all()
        for invitation in invitations:
            # Delete associated RSVPs
            RSVP.query.filter_by(invitation_id=invitation.id).delete()
            # Delete associated guest photos
            GuestPhoto.query.filter_by(invitation_id=invitation.id).delete()
            db.session.delete(invitation)
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        logging.info(f"Admin {current_user.email} deleted user {user.email} and {len(invitations)} invitations")
        return jsonify({"success": True, "message": f"User and {len(invitations)} invitations deleted"})
    except Exception as e:
        logging.error(f"Error deleting user: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/api/invitations', methods=['GET'])
@admin_required
def admin_api_invitations():
    """Get all invitations with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str)
        event_type = request.args.get('event_type', '', type=str)
        
        query = Invitation.query
        
        if search:
            query = query.filter(
                (Invitation.title.contains(search)) |
                (Invitation.family_name.contains(search)) |
                (Invitation.celebrant_name.contains(search))
            )
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        invitations = query.order_by(Invitation.date_created.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        invitations_data = [{
            'id': invitation.id,
            'title': invitation.title,
            'creator_email': invitation.author.email if invitation.author else 'Unknown',
            'creator_name': invitation.author.name if invitation.author else 'Unknown',
            'views': invitation.view_count,
            'rsvp_count': len(invitation.rsvps),
            'event_type': invitation.event_type,
            'vibe': invitation.vibe,
            'date_created': invitation.date_created.strftime('%Y-%m-%d %H:%M:%S'),
            'share_link': invitation.share_link
        } for invitation in invitations.items]
        
        return jsonify({
            "success": True,
            "invitations": invitations_data,
            "total": invitations.total,
            "page": page,
            "per_page": per_page,
            "pages": invitations.pages
        })
    except Exception as e:
        logging.error(f"Error fetching invitations: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/admin/api/invitations/<int:invitation_id>/delete', methods=['DELETE'])
@admin_required
def admin_api_delete_invitation(invitation_id):
    """Delete an invitation"""
    try:
        invitation = Invitation.query.get(invitation_id)
        if not invitation:
            return jsonify({"success": False, "error": "Invitation not found"}), 404
        
        # Delete associated RSVPs
        RSVP.query.filter_by(invitation_id=invitation_id).delete()
        # Delete associated guest photos
        GuestPhoto.query.filter_by(invitation_id=invitation_id).delete()
        
        # Delete the invitation
        db.session.delete(invitation)
        db.session.commit()
        
        logging.info(f"Admin {current_user.email} deleted invitation {invitation_id}")
        return jsonify({"success": True, "message": "Invitation deleted successfully"})
    except Exception as e:
        logging.error(f"Error deleting invitation: {str(e)}")
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
