import os
import logging
from flask import Flask, render_template
from flask_cors import CORS
import google.generativeai as genai
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, login_manager, oauth
from config import Config
from models import User

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Fix for Render/Heroku HTTPS
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Load Configuration
    app.config.from_object(Config)
    
    # Initialize Extensions
    CORS(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    oauth.init_app(app)
    
    # Configure Google OAuth
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
        access_token_url='https://oauth2.googleapis.com/token',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
        client_kwargs={'scope': 'openid email profile'},
    )
    
    # Configure Gemini AI
    if app.config['GEMINI_API_KEY']:
        genai.configure(api_key=app.config['GEMINI_API_KEY'])
        logging.info(f"✅ Gemini API key loaded")
    else:
        logging.error("⚠️ GEMINI_API_KEY not found!")

    # Register Blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.dashboard import dashboard_bp
    from routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    
    # User Loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Database Creation & Migration
    with app.app_context():
        db.create_all()
        run_migrations(app)
        
    return app

def run_migrations(app):
    """Run simple database migrations"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # Check if user table exists and if is_admin column exists
        if 'user' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'is_admin' not in columns:
                logging.info("Adding is_admin column to user table...")
                with db.engine.begin() as conn:
                    conn.execute(db.text('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL'))
                logging.info("✅ is_admin column added successfully")
        
        # Check Invitation table for new columns
        if 'invitation' in inspector.get_table_names():
            inv_columns = [col['name'] for col in inspector.get_columns('invitation')]
            
            new_columns = {
                'story': 'TEXT',
                'gallery_photos': 'TEXT',
                'voice_message_url': 'VARCHAR(500)',
                'share_link': 'VARCHAR(100)',
                'view_count': 'INTEGER DEFAULT 0'
            }
            
            with db.engine.begin() as conn:
                for col_name, col_type in new_columns.items():
                    if col_name not in inv_columns:
                        logging.info(f"Adding {col_name} column to invitation table...")
                        try:
                            conn.execute(db.text(f'ALTER TABLE invitation ADD COLUMN {col_name} {col_type}'))
                            logging.info(f"✅ {col_name} column added successfully")
                        except Exception as col_error:
                            logging.warning(f"Failed to add {col_name}: {col_error}")
    except Exception as e:
        if 'duplicate column' not in str(e).lower() and 'no such table' not in str(e).lower():
            logging.warning(f"Migration check: {e}")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
