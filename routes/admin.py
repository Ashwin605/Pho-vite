from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, logout_user
from extensions import db
from models import User, Invitation, RSVP, GuestPhoto
from utils import admin_required
from datetime import datetime, timedelta
import logging

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Redirect admin login to regular login page (single login for all users)"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.admin_dashboard'))
    # Redirect to regular login page
    return redirect(url_for('auth.login'))

@admin_bp.route('/logout')
@admin_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('Logged out from admin panel', 'success')
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/dashboard')
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
