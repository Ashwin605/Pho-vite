from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Invitation, RSVP
from datetime import datetime
import logging
import os
import json
import uuid
import google.generativeai as genai
import replicate
from services.email_service import EmailService

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
        
        model = genai.GenerativeModel('gemini-2.5-flash')
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
            return jsonify({"success": True, "data": result})
        except Exception as e:
            logging.error(f"Error parsing Gemini response: {e}")
            return jsonify({"success": False, "error": "Failed to generate prompt"}), 500

    except Exception as e:
        logging.error(f"Error in refine_prompt: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/generate-image', methods=['POST'])
@login_required
def generate_image():
    """Generate invitation image using Pollinations.AI (free) or Replicate AI"""
    try:
        data = request.json
        image_prompt = data.get('image_prompt')
        user_photo_url = data.get('user_photo_url')
        title = data.get('title', 'Untitled Invitation')
        body = data.get('body', '')
        event_type = data.get('eventType', 'General')
        vibe = data.get('vibe', 'General')
        
        # Additional fields for enhanced invitations
        family_name = data.get('family_name', '')
        celebrant_name = data.get('celebrant_name', '')
        event_date = data.get('event_date', '')
        event_time = data.get('event_time', '')
        event_venue = data.get('event_venue', '')
        event_message = data.get('event_message', '')
        location_name = data.get('location_name', '')
        gallery_photos = data.get('gallery_photos', [])
        
        logging.info(f"Generating image for user {current_user.id}. Photo URL provided: {bool(user_photo_url)}")

        output_url = ""
        
        # Check if Replicate API token is available
        replicate_token = os.getenv('REPLICATE_API_TOKEN')
        
        if replicate_token and user_photo_url:
            # Use InstantID for face swap/integration (requires Replicate)
            logging.info("Using InstantID via Replicate...")
            try:
                output = replicate.run(
                    "instantx/instant-id:c1e1e534d4e6c2396ca9f59d237d0c6562b391e38f4f65597255443662d27b2f",
                    input={
                        "image": user_photo_url,
                        "prompt": image_prompt,
                        "negative_prompt": "(lowres, low quality, worst quality:1.2), (text:1.2), watermark, glitch, deformed, mutated, cross-eyed, ugly, disfigured",
                        "style_name": "(No style)",
                        "num_inference_steps": 30,
                        "guidance_scale": 5,
                        "identity_scale": 0.8,
                        "adapter_scale": 0.8,
                        "enable_fast_process": True
                    }
                )
                if isinstance(output, list) and len(output) > 0:
                    output_url = output[0]
                else:
                    output_url = str(output)
            except Exception as replicate_err:
                logging.error(f"InstantID failed: {replicate_err}")
                # Fallback to Pollinations.AI
                output_url = ""
        
        # Use Pollinations.AI (free, no API key needed) as primary/fallback
        if not output_url:
            logging.info("Using Pollinations.AI for image generation...")
            try:
                import urllib.parse
                import hashlib
                
                # Clean and shorten the prompt for URL (max 400 chars to avoid URL issues)
                clean_prompt = image_prompt.replace('\n', ' ').replace('\r', ' ').strip()
                if len(clean_prompt) > 400:
                    clean_prompt = clean_prompt[:400] + "..."
                
                # Add style suffix for better results
                clean_prompt = f"{clean_prompt}, elegant invitation design, high quality, vibrant colors"
                
                encoded_prompt = urllib.parse.quote(clean_prompt, safe='')
                
                # Generate a seed based on prompt for consistency
                seed = int(hashlib.md5(image_prompt.encode()).hexdigest()[:8], 16) % 1000000
                
                # Pollinations.AI endpoint - generates image directly from URL
                output_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1536&nologo=true&seed={seed}"
                
                logging.info(f"Pollinations.AI URL generated: {output_url[:150]}...")
                
            except Exception as poll_err:
                logging.error(f"Pollinations.AI failed: {poll_err}")
                # Last resort fallback to Replicate Flux if available
                if replicate_token:
                    try:
                        logging.info("Falling back to Flux Schnell...")
                        output = replicate.run(
                            "black-forest-labs/flux-schnell",
                            input={
                                "prompt": image_prompt,
                                "num_outputs": 1,
                                "aspect_ratio": "9:16",
                                "output_format": "png",
                                "output_quality": 90
                            }
                        )
                        if isinstance(output, list) and len(output) > 0:
                            output_url = output[0]
                        else:
                            output_url = str(output)
                    except Exception as flux_err:
                        logging.error(f"Flux Schnell also failed: {flux_err}")
                        return jsonify({"success": False, "error": "Image generation failed. Please try again."}), 500
                else:
                    return jsonify({"success": False, "error": "Image generation failed. Please try again."}), 500
        
        # Generate unique share link
        share_link = str(uuid.uuid4())[:8]
        
        # Save to database
        invitation_id = None
        share_url = None
        try:
            new_invite = Invitation(
                title=title,
                body=body,
                image_url=output_url,
                event_type=event_type,
                vibe=vibe,
                user_id=current_user.id,
                family_name=family_name,
                celebrant_name=celebrant_name,
                event_date=event_date,
                event_time=event_time,
                event_venue=event_venue,
                event_message=event_message,
                location_name=location_name,
                share_link=share_link,
                gallery_photos=json.dumps(gallery_photos) if gallery_photos else None
            )
            db.session.add(new_invite)
            db.session.commit()
            invitation_id = new_invite.id
            share_url = f"/invite/{share_link}"
            logging.info(f"Saved invitation {new_invite.id} for user {current_user.id}")
        except Exception as db_e:
            logging.error(f"Failed to save to DB: {str(db_e)}")
            db.session.rollback()

        return jsonify({
            "success": True, 
            "image_url": output_url,
            "invitation_id": invitation_id,
            "share_link": share_url
        })

    except Exception as e:
        logging.error(f"Error in generate-image: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

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
            system_prompt += "\nThe user is currently on the creation page. You can help them fill out the form."
        elif context.get('context') == 'viewing_dashboard':
            system_prompt += "\nThe user is on their dashboard. You can help them navigate to create a new invitation."
        elif context.get('context') == 'landing_page':
            system_prompt += "\nThe user is on the home page. You can guide them to the creation page."

        system_prompt += """
        
        CRITICAL: You must return a JSON object. Do not return plain text.
        
        JSON Structure:
        {
            "response": "Your friendly text response here...",
            "action": {
                "type": "navigate" | "fill_form" | "trigger_generate" | "none",
                "payload": {} 
            }
        }
        
        Action specific payloads:
        1. type: "navigate"
           payload: { 
               "url": "/create" | "/dashboard" | "/",
               "prefill": { ... same as fill_form payload ... } (Optional)
           }
           Use this when the user is NOT on the correct page but has provided details. 
           Example: User on Home says "Create birthday invite for John".
           Action: Navigate to /create with prefill data for John/Birthday.
           
        2. type: "fill_form"
           payload: {
               "eventType": "Birthday" | "Wedding" | "Party" | "Corporate" | "Anniversary" | "Baby Shower",
               "celebrantName": "Name",
               "eventDate": "YYYY-MM-DD",
               "eventTime": "HH:MM",
               "eventVenue": "Location",
               "eventMessage": "Message",
               "vibe": "Theme Name",
               "companyName": "Company (for Corporate)",
               "partyName": "Event Name (for Party)",
               "babyName": "Baby Name",
               "brideName": "Bride Name",
               "groomName": "Groom Name"
           }
           Use this ONLY when the user is ALREADY on the creation page.
           
        3. type: "trigger_generate"
           payload: {}
           Use this when the user explicitly asks to "create", "generate", or "make" the invitation after providing details.
           
        4. type: "none"
           payload: {}
           Use this for general questions.
           payload: {}
           Use this when the user explicitly asks to "create", "generate", or "make" the invitation after providing details.
           
        4. type: "none"
           payload: {}
           Use this for general questions.
        """

        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(system_prompt + "\n\nUser Question: " + message)
        
        # Parse output
        import json
        try:
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.endswith('```'):
                text = text[:-3]
            ai_response = json.loads(text)
        except Exception as e:
            logging.error(f"Failed to parse AI JSON: {text}")
            ai_response = {
                "response": response.text,
                "action": {"type": "none"}
            }
        
        return jsonify({
            "success": True,
            "response": ai_response['response'],
            "action": ai_response.get('action')
        })

    except Exception as e:
        logging.error(f"Error in assistant_chat: {str(e)}")
        return jsonify({
            "success": False, 
            "error": "I encountered an error processing your request. Please try again."
        }), 500

@api_bp.route('/rsvp-submit', methods=['POST'])
def rsvp_submit():
    """Submit a new RSVP"""
    try:
        data = request.json
        invitation_id = data.get('invitationId')
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        status = data.get('status', 'attending')
        
        if not all([invitation_id, name]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
            
        # Check if invitation exists
        invitation = Invitation.query.get(invitation_id)
        if not invitation:
            return jsonify({"success": False, "error": "Invitation not found"}), 404
            
        # Create RSVP
        rsvp = RSVP(
            invitation_id=invitation_id,
            guest_name=name,
            guest_email=email,
            guest_message=message,
            status=status
        )
        
        db.session.add(rsvp)
        db.session.commit()
        
        # 📧 Send Emails asynchronously
        try:
            # 1. Notify Guest (Confirmation with Vibe Pass details)
            if email:
                share_link = f"{request.url_root}invite/{invitation.share_link}"
                EmailService.send_rsvp_confirmation(email, name, invitation.title, share_link)
                
            # 2. Notify Host (New registration)
            # Find host email
            host = invitation.author
            if host and host.email:
                EmailService.send_host_notification(host.email, name, message, invitation.title, status)
                
        except Exception as mail_error:
            # Don't fail the request if email fails, just log it
            logging.error(f"Failed to trigger emails: {mail_error}")
        
        return jsonify({
            "success": True, 
            "message": "RSVP submitted successfully!",
            "rsvp": {
                "name": name,
                "message": message,
                "status": status,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
        })
        
    except Exception as e:
        logging.error(f"Error in rsvp_submit: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/get-rsvps/<int:invite_id>', methods=['GET'])
def get_rsvps(invite_id):
    """Get all RSVPs for an invitation"""
    try:
        rsvps = RSVP.query.filter_by(invitation_id=invite_id).order_by(RSVP.date_responded.desc()).all()
        
        result = []
        for rsvp in rsvps:
            result.append({
                "name": rsvp.guest_name,
                "message": rsvp.guest_message,
                "status": rsvp.status,
                "date": rsvp.date_responded.strftime("%Y-%m-%d")
            })
            
        return jsonify({"success": True, "rsvps": result})
        
    except Exception as e:
        logging.error(f"Error getting RSVPs: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
