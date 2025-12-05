from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Invitation, RSVP
from datetime import datetime
import logging
import google.generativeai as genai

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@api_bp.route('/delete-invitation/<int:invite_id>', methods=['DELETE'])
@login_required
def delete_invitation(invite_id):
    """Delete an invitation"""
    try:
        logging.info(f"DELETE REQUEST: invite_id={invite_id} (type: {type(invite_id)})")
        
        invitation = Invitation.query.filter_by(id=invite_id).first()
        
        if not invitation:
            logging.error(f"❌ Invitation {invite_id} NOT FOUND in DB.")
            return jsonify({"success": False, "error": "Invitation not found"}), 404
        
        logging.info(f"✅ Invitation found: {invitation.id}, Title: {invitation.title}, User ID: {invitation.user_id}")
        
        if invitation.user_id != current_user.id:
            logging.error(f"⛔ Unauthorized delete attempt. User {current_user.id} tried to delete invite owned by {invitation.user_id}")
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Delete associated RSVPs first
        rsvp_count = RSVP.query.filter_by(invitation_id=invite_id).delete()
        logging.info(f"Deleted {rsvp_count} associated RSVPs")
        
        # Delete the invitation
        db.session.delete(invitation)
        db.session.commit()
        
        logging.info(f"🗑️ Successfully deleted invitation {invite_id}")
        return jsonify({"success": True, "message": "Invitation deleted successfully"})
    
    except Exception as e:
        logging.error(f"🔥 Error deleting invitation: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/update-invitation/<int:invite_id>', methods=['PUT'])
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

@api_bp.route('/refine-prompt', methods=['POST'])
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
        4. A short, heartwarming "Story" or "Memory" (2-3 sentences) that captures the essence of this event type and the people involved. This will be used for the event scrapbook.

        Return ONLY a JSON object with keys: "image_prompt", "card_title", "card_body", "story".
        
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
        
        (Examples omitted for brevity but implied)
        
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
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(system_prompt + "\n\n" + user_prompt)
        
        import json
        try:
            # Clean up response text to ensure it's valid JSON
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            
            result = json.loads(text)
            return jsonify(result)
        except Exception as e:
            logging.error(f"Error parsing Gemini response: {e}")
            return jsonify({"error": "Failed to generate prompt"}), 500

    except Exception as e:
        logging.error(f"Error in refine_prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/assistant-chat', methods=['POST'])
def assistant_chat():
    """Handle AI Assistant chat requests"""
    try:
        data = request.json
        message = data.get('message')
        context = data.get('context', {})
        
        if not message:
            return jsonify({"success": False, "error": "No message provided"}), 400
            
        logging.info(f"AI Assistant Chat: {message[:50]}... (Context: {context.get('context', 'unknown')})")
        
        # Construct system prompt based on context
        system_prompt = """
        You are the PhoVite AI Assistant, a helpful and friendly expert on creating digital event invitations.
        Your goal is to assist users in creating stunning invitations, navigating the platform, and answering questions about features.
        
        Platform Features:
        - Create custom invitations with AI-generated designs (borders/frames)
        - Upload personal photos to integrate into designs
        - Track RSVPs and guest messages
        - Share invitations via a unique link
        - Event types supported: Weddings, Birthdays, Parties, Corporate Events, Baby Showers, etc.
        - Vibes/Styles: Neon, Royal, Minimal, Floral, Retro, etc.
        
        Tone: Friendly, enthusiastic, professional, and concise. Use emojis occasionally.
        
        Context Awareness:
        """
        
        if context.get('context') == 'creating_invitation':
            system_prompt += "\nThe user is currently on the creation page. Offer specific design advice, help with prompt refinement, or explain form fields."
        elif context.get('context') == 'viewing_dashboard':
            system_prompt += "\nThe user is on their dashboard. Help them manage existing invites, check RSVPs, or start a new project."
        elif context.get('context') == 'landing_page':
            system_prompt += "\nThe user is on the home page. Explain what PhoVite is and encourage them to sign up or try the demo."
        else:
            system_prompt += "\nThe user is navigating the site. Be generally helpful."
            
        system_prompt += "\n\nProvide a helpful, direct answer to the user's question."

        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(system_prompt + "\n\nUser Question: " + message)
        
        return jsonify({
            "success": True,
            "response": response.text
        })

    except Exception as e:
        logging.error(f"Error in assistant_chat: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "I encountered an error processing your request. Please try again."
        }), 500
