from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Invitation

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user_invites = Invitation.query.filter_by(user_id=current_user.id).order_by(Invitation.date_created.desc()).all()
    return render_template('dashboard.html', invites=user_invites, user=current_user)

@dashboard_bp.route('/create')
@login_required
def create():
    return render_template('create.html')

@dashboard_bp.route('/edit/<int:invite_id>')
@login_required
def edit_invitation(invite_id):
    """Edit invitation page"""
    invitation = Invitation.query.get(invite_id)
    
    if not invitation:
        flash('Invitation not found', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    if invitation.user_id != current_user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('edit_invitation.html', invitation=invitation)
