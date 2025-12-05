from flask import Blueprint, render_template

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
