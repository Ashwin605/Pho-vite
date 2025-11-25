# Video Generation Guide

## Overview
The app can generate 10-15 second hype videos from your invitations with optional background music.

## How to Use

### Step 1: Generate an Invitation
1. Go to the **Create** page
2. Fill in all event details (name, date, venue, message, etc.)
3. Upload your photos
4. Click **"Generate PhoVite"**
5. Wait for the invitation to be generated and displayed

### Step 2: Generate Video
1. After the invitation preview appears, scroll down to the action buttons
2. Click **"Generate Hype Video (10-15s)"** button
3. A music selection modal will appear with options:
   - **Continue Without Music** - Generate video without background music
   - **Happy Birthday** - Upbeat & cheerful music
   - **Wedding Bells** - Romantic & elegant music
   - **Party Time** - Energetic & fun music
   - **Celebration** - Joyful & festive music
   - **Elegant Classic** - Sophisticated & classy music
   - **Upbeat Pop** - Modern & trendy music

4. Select your preferred option
5. Wait 30-60 seconds for the video to generate
6. Once complete, a **"Download Video"** button will appear
7. Click to download your video!

## Video Specifications
- **Duration**: 10-15 seconds (default: 12 seconds)
- **Format**: MP4 (H.264)
- **Resolution**: 1080x1920 (vertical/portrait - perfect for Instagram Stories, TikTok, Reels)
- **FPS**: 24 frames per second
- **Features**:
  - Your invitation image as background
  - Animated text overlays (title, message, location)
  - Fade-in effects for text
  - Optional background music

## Technical Details

### Requirements
- Python 3.x
- MoviePy (installed via requirements.txt)
- imageio-ffmpeg (bundled with MoviePy)
- Pillow (for image processing)

### Dependencies Installed
```
moviepy==1.0.3
imageio-ffmpeg==0.4.9
```

### Backend Endpoint
- **URL**: `/api/generate-video`
- **Method**: POST
- **Auth**: Required (login_required)
- **Payload**:
  ```json
  {
    "invitation_id": 123,
    "music": "happy_birthday",  // optional
    "duration": 12              // 10-15 seconds
  }
  ```

## Troubleshooting

### Video Not Generating?
1. **Check Console Logs**: Open browser console (F12) and look for errors
2. **Check Server Logs**: Look at your Flask server terminal for error messages
3. **Verify Invitation**: Make sure you generated an invitation first
4. **Check Permissions**: Ensure the `static/videos/` directory exists and is writable

### Common Issues
- **"No invitation found"**: Generate an invitation before clicking video button
- **"Server error"**: Check Flask logs for detailed error messages
- **Video takes too long**: Video generation takes 30-60 seconds - be patient!

### Server Logs
The video generation logs will show:
```
🎬 Video generation started
Video request - ID: 123, Music: happy_birthday, Duration: 12s
Step 1: Processing image...
Step 2: Creating 12s video clip...
Step 3: Compositing clips...
Step 4: Writing video file...
✅ Video file written successfully!
```

## File Locations
- Generated videos: `static/videos/hype_{invitation_id}_{timestamp}.mp4`
- Frontend JavaScript: `static/js/script-enhanced.js` (generateVideoWithMusic function)
- Backend route: `app.py` (generate_video function)
- UI button: `templates/create.html` (generateVideoBtn)

## Future Enhancements
- [ ] Add more music options
- [ ] Allow custom duration selection (slider)
- [ ] Add more animation effects (zoom, pan, transitions)
- [ ] Support for video backgrounds instead of images
- [ ] Add guest photos to video compilation
- [ ] Progress bar during generation
- [ ] Preview video before download

---

**Note**: Video generation requires significant processing. The first video may take slightly longer as MoviePy initializes.

