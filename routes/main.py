from flask import Blueprint, render_template, abort
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/help')
def help_center():
    return render_template('help.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@main_bp.route('/invite/<share_link>')
def view_invite(share_link):
    """Public invitation view page"""
    from models import Invitation, db
    
    # Find the invitation by share_link
    invitation = Invitation.query.filter_by(share_link=share_link).first()
    
    if not invitation:
        abort(404)
    
    # Increment view count
    invitation.view_count = (invitation.view_count or 0) + 1
    db.session.commit()
    
    # Parse gallery photos if stored as JSON
    gallery_photos = []
    if invitation.gallery_photos:
        try:
            gallery_photos = json.loads(invitation.gallery_photos)
        except (json.JSONDecodeError, TypeError):
            gallery_photos = []
    
    return render_template('public_invite.html', 
                         invitation=invitation, 
                         gallery_photos=gallery_photos)
