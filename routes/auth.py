from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, oauth
from models import User
from config import Config
import secrets
import requests
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        logging.info(f"Login attempt for email: {email}")
        
        # Check if this is an admin login (check plain password first)
        if Config.ADMIN_EMAIL and Config.ADMIN_PASSWORD:
            email_match = email.lower() == Config.ADMIN_EMAIL.lower()
            password_match = password == Config.ADMIN_PASSWORD
            
            logging.info(f"Admin check - Email match: {email_match}, Password match: {password_match}")
            
            if email_match and password_match:
                # Find or create admin user
                user = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
                if not user:
                    # Create admin user if doesn't exist
                    user = User(
                        email=Config.ADMIN_EMAIL,
                        name='Admin',
                        password=generate_password_hash(Config.ADMIN_PASSWORD, method='pbkdf2:sha256'),
                        is_admin=True
                    )
                    db.session.add(user)
                    db.session.commit()
                    logging.info(f"Created new admin user: {Config.ADMIN_EMAIL}")
                else:
                    # Update existing user to be admin
                    user.is_admin = True
                    # Always update password to match current admin password
                    user.password = generate_password_hash(Config.ADMIN_PASSWORD, method='pbkdf2:sha256')
                    db.session.commit()
                    logging.info(f"Updated user to admin: {Config.ADMIN_EMAIL}")
                
                login_user(user)
                logging.info(f"Admin login successful: {email}")
                return redirect(url_for('admin.admin_dashboard'))
        
        # Regular user login
        user = User.query.filter_by(email=email).first()
        if user and user.password and check_password_hash(user.password, password):
            login_user(user)
            # Redirect to admin dashboard if user is admin, otherwise regular dashboard
            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            return redirect(url_for('dashboard.dashboard'))
        else:
            logging.warning(f"Failed login attempt for: {email}")
            flash('Invalid email or password', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
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
            return redirect(url_for('dashboard.dashboard'))
    return render_template('auth/signup.html')


@auth_bp.route('/login/google')
def google_login():
    if not current_app.config['GOOGLE_CLIENT_ID'] or "your_google_client_id" in current_app.config['GOOGLE_CLIENT_ID']:
        flash('Google Login is not configured. Please set GOOGLE_CLIENT_ID in .env', 'error')
        return redirect(url_for('auth.login'))
        
    google = oauth.create_client('google')
    redirect_uri = url_for('auth.google_authorize', _external=True)
    
    # Force http if running locally to match the callback logic
    if 'localhost' in redirect_uri or '127.0.0.1' in redirect_uri:
        redirect_uri = redirect_uri.replace('https://', 'http://')
        
    logging.info(f"Initiating Google Login. Redirect URI: {redirect_uri}")
    return google.authorize_redirect(redirect_uri)

@auth_bp.route('/login/google/callback')
def google_authorize():
    try:
        # Manual Token Exchange to Debug/Fix invalid_client
        code = request.args.get('code')
        if not code:
            flash('No code received from Google', 'error')
            return redirect(url_for('auth.login'))

        token_url = "https://oauth2.googleapis.com/token"
        # Determine the redirect URI used in the request
        redirect_uri = url_for('auth.google_authorize', _external=True)
        
        # Force http if running locally and behind a proxy that might report https
        if 'localhost' in redirect_uri or '127.0.0.1' in redirect_uri:
            redirect_uri = redirect_uri.replace('https://', 'http://')

        payload = {
            'code': code,
            'client_id': current_app.config['GOOGLE_CLIENT_ID'],
            'client_secret': current_app.config['GOOGLE_CLIENT_SECRET'],
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }

        # Debug Logging for Credentials
        curr_client_id = payload['client_id']
        curr_client_secret = payload['client_secret']
        masked_id = f"{curr_client_id[:10]}...{curr_client_id[-5:]}" if curr_client_id else "None"
        masked_secret = f"{curr_client_secret[:5]}...{curr_client_secret[-3:]}" if curr_client_secret else "None"
        
        logging.info("--- MANUAL TOKEN EXCHANGE ---")
        logging.info(f"Using Client ID: {masked_id}")
        logging.info(f"Using Client Secret: {masked_secret}")
        logging.info(f"Sending token request to: {token_url}")
        logging.info(f"Payload Client ID: {payload['client_id']}")
        logging.info(f"Payload Redirect URI: {payload['redirect_uri']}")
        
        resp = requests.post(token_url, data=payload)
        
        if resp.status_code != 200:
            error_data = resp.json()
            error_msg = error_data.get('error_description') or error_data.get('error') or 'Unknown error'
            error_msg = error_data.get('error_description') or error_data.get('error') or 'Unknown error'
            flash(f'Google Login Failed: {error_msg}. \nID: {masked_id} \nSecret: {masked_secret} \nRedirect URI: {redirect_uri}', 'error')
            return redirect(url_for('auth.login'))

        token_data = resp.json()
        access_token = token_data.get('access_token')
        
        # Get User Info
        user_info_resp = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_resp.status_code != 200:
            flash('Failed to fetch user info from Google', 'error')
            return redirect(url_for('auth.login'))
            
        user_info = user_info_resp.json()
        
        if not user_info.get('email'):
            flash('Failed to get email from Google.', 'error')
            return redirect(url_for('auth.login'))

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
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('dashboard.dashboard'))

    except Exception as e:
        logging.error(f"Google Login Error: {str(e)}")
        flash(f'Google Login Failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
