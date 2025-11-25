# PhoVite Version 1.0 - Feature Master List

## 🚀 Core Value Proposition
**"Turn Moments into Unforgettable Invites"**
PhoVite is not just an image generator; it's a social experience platform. It transforms a simple event invitation into a hype-building, interactive moment.

---

## 1. 🎨 AI-Powered Creation Suite (Existing & Refined)
The heart of the application.
- **Text-to-Vibe Engine:** Users describe their event (e.g., "Neon birthday on a rooftop"), and Gemini AI converts it into a highly detailed artistic prompt.
- **Instant Image Generation:** Uses Flux/SDXL (via Pollinations/HuggingFace) to generate professional-grade background visuals.
- **Smart Details Extraction:** Automatically pulls Date, Time, and Venue from natural language input.
- **Photo Integration:** Seamlessly blends the user's uploaded photo into the AI-generated background using smart masking and overlays.
- **Typography Engine:** Auto-selects fonts and layouts (Gold/Neon/Minimal) based on the chosen vibe.
- **✏️ Live Editor (NEW):**
  - **Real-time Preview:** See changes instantly before finalizing.
  - **Font Customization:** Swap between curated font styles (Modern, Classic, Handwritten).
  - **Text Tweaks:** Edit the Title, Body, Date, and Venue text directly.
  - **Style Adjustments:** Toggle text colors (White/Black/Gold) for better readability.

## 2. 📹 AI Video "Hype" Stories (NEW - To Build)
Transform the static invite into a 15-second vertical video optimized for Instagram Stories, TikTok, and WhatsApp Status.
- **Motion Poster:** Adds "Ken Burns" (pan/zoom) effects to the static invitation.
- **Dynamic Overlays:** Animated text for "You're Invited", Date, and Time.
- **Audio-Reactive:** Background music automatically selected based on the Vibe (e.g., *Cyberpunk* gets Synthwave, *Wedding* gets Orchestral).
- **One-Click Download:** Generates an `.mp4` file ready for social sharing.

## 3. ✅ The "Vibe Check" RSVP (NEW - Standout Feature)
Replace the boring "Yes/No" form with an interactive game.
- **Selfie RSVP:** Guests confirm attendance by uploading a selfie.
- **Vibe Pass Generation:** The system generates a personalized "Ticket" for the guest, applying the event's style filters to their selfie.
- **Social Proof:** Guests are encouraged to share their "Vibe Pass" on social media, creating free marketing and FOMO for the event.

## 4. 🌐 The "Live" Invitation Page (Existing & Enhanced)
A dedicated, shareable web page for every event.
- **Personal Voice Message:** Host can record a 15s audio greeting (e.g., "Hey guys, can't wait to see you!").
- **Memory Lane Gallery:** A grid of 4-8 photos showing the host's journey or past events.
- **Smart Maps:** Integrated Google Maps button for one-click navigation.
- **Calendar Integration:** "Add to Calendar" button (Google/Apple/Outlook).
- **View Counter:** Shows the host how many people have viewed the invite.

## 5. 🔐 User System & Security (Existing)
- **Google OAuth:** One-tap login/signup.
- **Mobile Verification:** OTP-based mobile number verification for security.
- **Dashboard:** Central hub to manage all created invites and view RSVPs.
- **Privacy Controls:** Unique, obscure share links (e.g., `phovite.com/invite/x7k9m2p`) to keep events private.

---

## 🛠 Tech Stack for V1
- **Frontend:** HTML5, TailwindCSS, Vanilla JS (for maximum speed/compatibility).
- **Backend:** Flask (Python).
- **Database:** SQLite (Dev) / PostgreSQL (Prod).
- **AI Models:** 
  - Text: Gemini Pro 1.5
  - Image: Flux / SDXL
- **Video Processing:** MoviePy (Server-side rendering).
- **Storage:** Local (Dev) / S3 or Uploadcare (Prod).
