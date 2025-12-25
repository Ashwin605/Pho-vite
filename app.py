import os
import logging
import json
import uuid
import secrets
import requests
import hashlib
import traceback
import urllib.parse
from datetime import datetime, timedelta
from functools import wraps
from threading import Thread
import tempfile
import requests
                      
# MoviePy imports with error handling since it can be heavy
try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
except ImportError:
    logging.warning("MoviePy not installed. Video generation will be disabled.")
    ImageClip = None

from flask import Flask, Blueprint, render_template, render_template_string, request, redirect, url_for, flash, current_app, abort, jsonify
import re
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_compress import Compress
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import google.generativeai as genai
import replicate
from services.email_service import EmailService

# --- 1. CONFIGURATION ---
load_dotenv(override=True)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '').strip()
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
    JAMENDO_CLIENT_ID = os.getenv('JAMENDO_CLIENT_ID', 'cc68060f')
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///vibecheck.db')
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'ashwinsrichandra2008@gmail.com').strip()
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'ashwin@2008').strip()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@phovite.com')

    # Performance
    SEND_FILE_MAX_AGE_DEFAULT = 31536000
    COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

# --- 2. EXTENSIONS ---

db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
compress = Compress()
from extensions import mail

# --- 3. MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=True)
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
    
    family_name = db.Column(db.String(200), nullable=True)
    celebrant_name = db.Column(db.String(200), nullable=True)
    event_date = db.Column(db.String(100), nullable=True)
    event_time = db.Column(db.String(100), nullable=True)
    event_venue = db.Column(db.String(300), nullable=True)
    event_message = db.Column(db.Text, nullable=True)
    gallery_photos = db.Column(db.Text, nullable=True)
    
    bride_name = db.Column(db.String(200), nullable=True)
    groom_name = db.Column(db.String(200), nullable=True)
    bride_photo = db.Column(db.Text, nullable=True)
    groom_photo = db.Column(db.Text, nullable=True)
    celebrant_photo = db.Column(db.Text, nullable=True)
    couple_names = db.Column(db.String(400), nullable=True)
    baby_name = db.Column(db.String(200), nullable=True)
    baby_gender = db.Column(db.String(50), nullable=True)
    company_name = db.Column(db.String(200), nullable=True)
    location_name = db.Column(db.String(200), nullable=True)
    location_address = db.Column(db.String(500), nullable=True)
    location_lat = db.Column(db.Float, nullable=True)
    location_lng = db.Column(db.Float, nullable=True)
    voice_message_url = db.Column(db.String(500), nullable=True)
    share_link = db.Column(db.String(100), unique=True, nullable=True)
    view_count = db.Column(db.Integer, default=0)
    story = db.Column(db.Text, nullable=True)
    rsvps = db.relationship('RSVP', backref='invitation', lazy=True)

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invitation_id = db.Column(db.Integer, db.ForeignKey('invitation.id'), nullable=False)
    guest_name = db.Column(db.String(150), nullable=False)
    guest_email = db.Column(db.String(150), nullable=True)
    guest_message = db.Column(db.Text, nullable=True)
    selfie_url = db.Column(db.String(500), nullable=True)
    vibe_pass_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(50), default='attending')
    date_responded = db.Column(db.DateTime, default=datetime.utcnow)

class GuestPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invitation_id = db.Column(db.Integer, db.ForeignKey('invitation.id'), nullable=False)
    guest_name = db.Column(db.String(150), nullable=False)
    photo_url = db.Column(db.String(500), nullable=False)
    message = db.Column(db.Text, nullable=True)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)

# --- 4. UTILITIES ---
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- 5. SERVICES ---
class EmailService:
    @staticmethod
    def _send_async_email(app, msg):
        with app.app_context():
            try:
                mail.send(msg)
                logging.info(f"📧 Email sent successfully to {msg.recipients}")
            except Exception as e:
                logging.error(f"🔥 Failed to send email to {msg.recipients}: {str(e)}")

    @staticmethod
    def send_email(subject, recipients, html_body, sender=None):
        app = current_app._get_current_object()
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            logging.warning("⚠️ Email configuration missing. Skipping email send.")
            return False
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_body,
            sender=sender or app.config.get('MAIL_DEFAULT_SENDER')
        )
        thr = Thread(target=EmailService._send_async_email, args=(app, msg))
        thr.start()
        return True

    @staticmethod
    def send_rsvp_confirmation(guest_email, guest_name, event_name, share_link):
        subject = f"You're on the list! RSVP Confirmed for {event_name}"
        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">You're In! 🎉</h1>
            </div>
            <div style="border: 1px solid #ddd; padding: 30px; border-radius: 0 0 10px 10px; background: #fff;">
                <p>Hi <strong>{guest_name}</strong>,</p>
                <p>Thanks for RSVPing ensuring you'll be there for <strong>{event_name}</strong>!</p>
                <div style="background: #f4f6f8; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                    <a href="{share_link}" style="display: inline-block; background: #764ba2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; margin-top: 10px; font-weight: bold;">View Invitation</a>
                </div>
                <p>See you there!</p>
            </div>
        </div>
        """
        return EmailService.send_email(subject, guest_email, html_body)

    @staticmethod
    def send_host_notification(host_email, guest_name, guest_message, event_name, status='attending'):
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
            </div>
        </div>
        """
        return EmailService.send_email(subject, host_email, html_body)

# --- 6. BLUEPRINTS ---

# --- MAIN BLUEPRINT ---
main_bp = Blueprint('main', __name__)
@main_bp.route('/')
def index(): return render_template('index.html')
@main_bp.route('/terms')
def terms(): return render_template('terms.html')
@main_bp.route('/about')
def about(): return render_template('about.html')
@main_bp.route('/privacy')
def privacy(): return render_template('privacy.html')
@main_bp.route('/help')
def help_center(): return render_template('help.html')
@main_bp.route('/contact')
def contact(): return render_template('contact.html')
@main_bp.route('/tutorial')
def tutorial(): return render_template('tutorial.html')

@main_bp.route('/invite/<share_link>')
def view_invite(share_link):
    invitation = Invitation.query.filter_by(share_link=share_link).first_or_404()
    invitation.view_count = (invitation.view_count or 0) + 1
    db.session.commit()
    gallery_photos = []
    if invitation.gallery_photos:
        try: gallery_photos = json.loads(invitation.gallery_photos)
        except: gallery_photos = []
    return render_template('public_invite.html', invitation=invitation, gallery_photos=gallery_photos)

# --- AUTH BLUEPRINT ---
auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if Config.ADMIN_EMAIL and email.lower() == Config.ADMIN_EMAIL.lower() and password == Config.ADMIN_PASSWORD:
            user = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
            if not user:
                user = User(email=Config.ADMIN_EMAIL, name='Admin', password=generate_password_hash(Config.ADMIN_PASSWORD), is_admin=True)
                db.session.add(user)
                db.session.commit()
            else:
                user.is_admin = True
                user.password = generate_password_hash(Config.ADMIN_PASSWORD)
                db.session.commit()
            login_user(user)
            return redirect(url_for('admin.admin_dashboard'))
        user = User.query.filter_by(email=email).first()
        if user and user.password and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin.admin_dashboard') if user.is_admin else url_for('dashboard.dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email, name, password = request.form.get('email'), request.form.get('name'), request.form.get('password')
        if User.query.filter_by(email=email).first(): flash('Email already exists', 'error')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard.dashboard'))
    return render_template('auth/signup.html')

@auth_bp.route('/login/google')
def google_login():
    google = oauth.create_client('google')
    redirect_uri = url_for('auth.google_authorize', _external=True)
    if 'localhost' in redirect_uri or '127.0.0.1' in redirect_uri: redirect_uri = redirect_uri.replace('https://', 'http://')
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/callback')
def google_authorize():
    try:
        code = request.args.get('code')
        redirect_uri = url_for('auth.google_authorize', _external=True)
        if 'localhost' in redirect_uri or '127.0.0.1' in redirect_uri: redirect_uri = redirect_uri.replace('https://', 'http://')
        resp = requests.post("https://oauth2.googleapis.com/token", data={
            'code': code, 'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'redirect_uri': redirect_uri, 'grant_type': 'authorization_code'
        })
        token_data = resp.json()
        user_info = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={'Authorization': f"Bearer {token_data['access_token']}"}).json()
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            user = User(email=user_info['email'], name=user_info['name'], google_id=user_info['sub'], profile_pic=user_info.get('picture'), password=generate_password_hash(secrets.token_urlsafe(16)))
            db.session.add(user)
        else:
            user.google_id, user.profile_pic = user_info['sub'], user_info.get('picture')
        db.session.commit()
        login_user(user)
        return redirect(url_for('admin.admin_dashboard') if user.is_admin else url_for('dashboard.dashboard'))
    except Exception as e:
        flash(f'Google Login Failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# --- DASHBOARD BLUEPRINT ---
dashboard_bp = Blueprint('dashboard', __name__)
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user_invites = Invitation.query.filter_by(user_id=current_user.id).order_by(Invitation.date_created.desc()).all()
    return render_template('dashboard.html', invites=user_invites, user=current_user)

@dashboard_bp.route('/create')
@login_required
def create(): return render_template('create.html')

@dashboard_bp.route('/edit/<int:invite_id>')
@login_required
def edit_invitation(invite_id):
    invitation = Invitation.query.get_or_404(invite_id)
    if invitation.user_id != current_user.id: return redirect(url_for('dashboard.dashboard'))
    return render_template('edit_invitation.html', invitation=invitation)

# --- ADMIN BLUEPRINT ---
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_invitations': Invitation.query.count(),
        'total_rsvps': RSVP.query.count(),
        'total_views': db.session.query(db.func.sum(Invitation.view_count)).scalar() or 0,
        'recent_invitations': Invitation.query.order_by(Invitation.date_created.desc()).limit(10).all(),
        'all_users': User.query.all()
    }
    return render_template('admin/dashboard.html', **stats)

# --- API BLUEPRINT ---
api_bp = Blueprint('api', __name__, url_prefix='/api')
@api_bp.route('/health')
def health_check(): return jsonify({"status": "ok"})

@api_bp.route('/delete-invitation/<int:invite_id>', methods=['DELETE'])
@login_required
def delete_invitation(invite_id):
    invitation = Invitation.query.get_or_404(invite_id)
    if invitation.user_id != current_user.id: return jsonify({"success": False}), 403
    RSVP.query.filter_by(invitation_id=invite_id).delete()
    db.session.delete(invitation)
    db.session.commit()
    return jsonify({"success": True})

@api_bp.route('/refine-prompt', methods=['POST'])
@login_required
def refine_prompt():
    data = request.json
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        sys_p = "Generate a JSON with keys image_prompt, card_title, card_body, story for an elegant invitation border."
        usr_p = f"Event: {data.get('eventType')}, Vibe: {data.get('vibe')}, Details: {data.get('details')}"
        resp = model.generate_content(sys_p + "\n" + usr_p)
        
        text = resp.text.strip()
        # Robust JSON extraction
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
            return jsonify({"success": True, "data": json.loads(text)})
        else:
             # Fallback if no JSON found, log it
            logging.error(f"No JSON found in response: {text}")
            return jsonify({"success": False, "error": "Invalid response from AI"}), 500
            
    except Exception as e:
        logging.error(f"Refine Prompt Error (Using Fallback): {str(e)}")
        # Fallback Logic: Generate valid data without AI
        fallback_data = {
            "image_prompt": f"A beautiful {data.get('vibe')} style background for a {data.get('eventType')} invitation, high quality, elegant design, 4k",
            "card_title": f"{data.get('eventType')} Celebration",
            "card_body": f"Please join us for a special {data.get('eventType')} celebration! We would be honored by your presence.",
            "story": f"Celebrating a special moment with a {data.get('vibe')} theme."
        }
        return jsonify({"success": True, "data": fallback_data})

@api_bp.route('/generate-image', methods=['POST'])
@login_required
def generate_image():
    data = request.json
    image_prompt = data.get('image_prompt')
    encoded_prompt = urllib.parse.quote(image_prompt[:400], safe='')
    seed = int(hashlib.md5(image_prompt.encode()).hexdigest()[:8], 16) % 1000000
    output_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1536&seed={seed}"
    share_link = str(uuid.uuid4())[:8]
    new_invite = Invitation(
        title=data.get('title'), body=data.get('body'), image_url=output_url,
        event_type=data.get('eventType'), vibe=data.get('vibe'), user_id=current_user.id,
        share_link=share_link, gallery_photos=json.dumps(data.get('gallery_photos', []))
    )
    db.session.add(new_invite)
    db.session.commit()
    
    # Send email notification
    try:
        share_full_url = url_for('main.view_invite', share_link=share_link, _external=True)
        EmailService.send_generation_notification(
            user_email=current_user.email,
            user_name=current_user.name,
            event_type=new_invite.event_type,
            share_link=share_full_url
        )
    except Exception as e:
        logging.error(f"Failed to send generation email: {str(e)}")
        
    return jsonify({"success": True, "image_url": output_url, "invitation_id": new_invite.id, "share_link": share_link})

@api_bp.route('/assistant-chat', methods=['POST'])
def assistant_chat():
    data = request.json
    model = genai.GenerativeModel('gemini-2.0-flash')
    resp = model.generate_content(f"User message: {data.get('message')}. Respond in JSON with keys 'response' and 'action'.")
    try:
        text = resp.text.strip()
        if text.startswith('```json'): text = text[7:-3]
        return jsonify({"success": True, **json.loads(text)})
    except Exception as e:
        logging.error(f"Assistant Chat Error (Using Fallback): {str(e)}")
        fallback_response = "I'm currently experiencing high traffic, but I'm here to help! You can use the buttons below to navigate."
        return jsonify({"success": True, "response": fallback_response, "action": {"type": "none"}})

@api_bp.route('/rsvp-submit', methods=['POST'])
def rsvp_submit():
    data = request.json
    invitation = Invitation.query.get_or_404(data.get('invitationId'))
    rsvp = RSVP(invitation_id=invitation.id, guest_name=data.get('name'), guest_email=data.get('email'), guest_message=data.get('message'), status=data.get('status', 'attending'))
    db.session.add(rsvp)
    db.session.commit()
    try:
        if data.get('email'): EmailService.send_rsvp_confirmation(data.get('email'), data.get('name'), invitation.title, f"{request.url_root}invite/{invitation.share_link}")
        if invitation.author.email: EmailService.send_host_notification(invitation.author.email, data.get('name'), data.get('message'), invitation.title, data.get('status'))
    except: pass
    return jsonify({"success": True})

@api_bp.route('/get-invitation-id-by-link/<share_link>')
def get_invitation_by_link(share_link):
    invitation = Invitation.query.filter_by(share_link=share_link).first()
    if not invitation:
        return jsonify({"success": False, "error": "Invitation not found"}), 404
    return jsonify({"success": True, "invitation_id": invitation.id})

@api_bp.route('/upload-voice', methods=['POST'])
@login_required
def upload_voice():
    if 'voice' not in request.files:
        return jsonify({"success": False, "error": "No voice file provided"}), 400
    
    file = request.files['voice']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if file:
        filename = f"voice_{uuid.uuid4().hex[:8]}.mp3"
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'voice')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        voice_url = url_for('static', filename=f'uploads/voice/{filename}')
        return jsonify({"success": True, "voice_url": voice_url})
        
    return jsonify({"success": False, "error": "Upload failed"}), 500

@api_bp.route('/enhance-invitation', methods=['POST'])
@login_required
def enhance_invitation():
    data = request.json
    invitation_id = data.get('invitation_id')
    voice_url = data.get('voice_message_url')
    
    invitation = Invitation.query.get_or_404(invitation_id)
    if invitation.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
        
    invitation.voice_message_url = voice_url
    db.session.commit()
    
    return jsonify({"success": True})

@api_bp.route('/generate-video', methods=['POST'])
@login_required
def generate_video():
    if not ImageClip:
        return jsonify({"success": False, "error": "Video generation not supported on this server"}), 501
    
    img_temp = None
    audio_temp = None
    
    try:
        data = request.json
        invite_id = data.get('invitation_id')
        music_key = data.get('music')
        duration = int(data.get('duration', 12))
        
        logging.info(f"Video Generation Request: ID={invite_id}, Music={music_key}")
        
        invitation = Invitation.query.get_or_404(invite_id)
        
        # Ensure static/videos exists
        video_dir = os.path.join(current_app.root_path, 'static', 'videos')
        os.makedirs(video_dir, exist_ok=True)
        
        # 1. Get Image
        # Create temp file but CLOSE it immediately so other processes/methods can open it freely on Windows
        img_fd, img_path = tempfile.mkstemp(suffix='.png')
        os.close(img_fd) # Close the file descriptor immediately
        img_temp = img_path # Store path for cleanup
        
        image_url = invitation.image_url
        
        if image_url.startswith('http'):
            resp = requests.get(image_url, stream=True, timeout=10)
            if resp.status_code == 200:
                with open(img_path, 'wb') as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
            else:
                return jsonify({"success": False, "error": f"Failed to download image: {resp.status_code}"}), 400
        elif image_url.startswith('/static'):
            local_path = os.path.join(current_app.root_path, image_url.lstrip('/'))
            # Copy to temp path
            with open(local_path, 'rb') as src, open(img_path, 'wb') as dst:
                dst.write(src.read())
        else:
             return jsonify({"success": False, "error": "Invalid image URL format"}), 400
             
        # 2. Get Audio
        if music_key:
            music_map = {
                'happy_birthday': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-1.mp3',
                'wedding_bells': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-2.mp3',
                'party_time': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-3.mp3',
                'celebration': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-4.mp3',
                'elegant_classic': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-5.mp3',
                'upbeat_pop': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-6.mp3'
            }
            music_url = music_map.get(music_key)
            if music_url:
                audio_fd, audio_path = tempfile.mkstemp(suffix='.mp3')
                os.close(audio_fd) 
                audio_temp = audio_path
                
                headers = {'User-Agent': 'Mozilla/5.0'}
                try:
                    resp = requests.get(music_url, headers=headers, stream=True, timeout=15)
                    if resp.status_code == 200:
                        with open(audio_path, 'wb') as f:
                            for chunk in resp.iter_content(1024):
                                f.write(chunk)
                    else:
                        logging.warning(f"Failed to download music {music_url}")
                        try: os.unlink(audio_path) 
                        except: pass
                        audio_temp = None
                except Exception as e:
                    logging.error(f"Music download error: {e}")
                    try: os.unlink(audio_path) 
                    except: pass
                    audio_temp = None

        # 3. Generate with MoviePy
        try:
            # Create video clip
            # Using ImageClip with the path
            clip = ImageClip(img_temp).set_duration(duration)
            
            # RESIZE to even dimensions to prevent libx264 errors
            # Only resize if necessary to preserve quality, but ensure mod 2
            w, h = clip.size
            new_w = w if w % 2 == 0 else w - 1
            new_h = h if h % 2 == 0 else h - 1
            if new_w != w or new_h != h:
                clip = clip.resize(newsize=(new_w, new_h))

            # Add audio if present
            if audio_temp:
                try:
                    audio = AudioFileClip(audio_temp)
                    if audio.duration > duration:
                        audio = audio.subclip(0, duration)
                    
                    audio = audio.audio_fadeout(2)
                    clip = clip.set_audio(audio)
                except Exception as e:
                    logging.error(f"Audio clip error: {e}")

            # Generate Output Filename
            filename = f"hype_{invite_id}_{uuid.uuid4().hex[:8]}.mp4"
            output_path = os.path.join(video_dir, filename)
            
            # Write file
            # IMPORTANT: codec='libx264' + ffmpeg_params=['-pix_fmt', 'yuv420p'] ensures browser compatibility
            # removing 'audio_codec'='aac' if no audio to prevent errors, or letting moviepy handle it
            write_kwargs = {
                'fps': 24,
                'codec': 'libx264',
                'preset': 'ultrafast',
                'ffmpeg_params': ['-pix_fmt', 'yuv420p'],
                'logger': None
            }
            if clip.audio:
                write_kwargs['audio_codec'] = 'aac'
            
            clip.write_videofile(output_path, **write_kwargs)
            
            # Cleanup Clips
            try: clip.close() 
            except: pass
            if 'audio' in locals() and audio:
                try: audio.close()
                except: pass
                
            video_url = url_for('static', filename=f'videos/{filename}')
            return jsonify({"success": True, "video_url": video_url})
            
        except Exception as e:
            logging.error(f"MoviePy Generation Error: {str(e)}\n{traceback.format_exc()}")
            return jsonify({"success": False, "error": f"Video generation failed: {str(e)}"}), 500
            
    except Exception as e:
        logging.error(f"Video Generation Setup Error: {str(e)}")
        return jsonify({"success": False, "error": f"Setup failed: {str(e)}"}), 500
    finally:
        # Clean up temp files
        try:
            if img_temp and os.path.exists(img_temp): os.unlink(img_temp)
            if audio_temp and os.path.exists(audio_temp): os.unlink(audio_temp)
        except: pass

@api_bp.errorhandler(Exception)
def handle_api_error(e):
    logging.error(f"API Error: {str(e)}")
    # If it's an HTTP error (like 404), use its code, otherwise 500
    code = 500
    if hasattr(e, 'code'):
        code = e.code
    return jsonify({"success": False, "error": str(e)}), code

# --- 7. APP FACTORY ---
def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    oauth.init_app(app)
    compress.init_app(app)
    mail.init_app(app)
    
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    if app.config['GEMINI_API_KEY']: genai.configure(api_key=app.config['GEMINI_API_KEY'])
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)


    
    @app.template_filter('google_calendar_dates')
    def google_calendar_dates_filter(invitation):
        try:
            if not invitation.event_date or not invitation.event_time:
                return ""
            # Cleanup input string to ensure it matches format
            date_clean = invitation.event_date.strip()
            time_clean = invitation.event_time.strip()
            dt_str = f"{date_clean} {time_clean}"
            start_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M") 
            end_dt = start_dt + timedelta(hours=4)
            return f"{start_dt.strftime('%Y%m%dT%H%M00')}/{end_dt.strftime('%Y%m%dT%H%M00')}"
        except Exception as e:
            logging.error(f"Date parsing error for calendar: {e}")
            return ""

    @login_manager.user_loader
    def load_user(user_id): return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)