// Event-specific theme configurations
const EVENT_THEMES = {
    'Birthday': [
        { name: 'Neon Party', emoji: '⚡', value: 'Neon Party' },
        { name: 'Balloon Fest', emoji: '🎈', value: 'Balloon Fest' },
        { name: 'Confetti Pop', emoji: '🎊', value: 'Confetti Pop' },
        { name: 'Cake Dreams', emoji: '🎂', value: 'Cake Dreams' }
    ],
    'Wedding': [
        { name: 'Royal Elegance', emoji: '👑', value: 'Royal Elegance' },
        { name: 'Floral Romance', emoji: '🌸', value: 'Floral Romance' },
        { name: 'Classic White', emoji: '🤍', value: 'Classic White' },
        { name: 'Garden Dream', emoji: '🌿', value: 'Garden Dream' }
    ],
    'Party': [
        { name: 'Disco Lights', emoji: '🪩', value: 'Disco Lights' },
        { name: 'Beach Vibes', emoji: '🏖️', value: 'Beach Vibes' },
        { name: 'Retro Funk', emoji: '🕺', value: 'Retro Funk' },
        { name: 'Glow Party', emoji: '💫', value: 'Glow Party' }
    ],
    'Corporate': [
        { name: 'Professional', emoji: '💼', value: 'Professional' },
        { name: 'Modern Tech', emoji: '💻', value: 'Modern Tech' },
        { name: 'Luxury Gold', emoji: '✨', value: 'Luxury Gold' },
        { name: 'Minimal Clean', emoji: '⚪', value: 'Minimal Clean' }
    ],
    'Anniversary': [
        { name: 'Romantic Rose', emoji: '🌹', value: 'Romantic Rose' },
        { name: 'Golden Years', emoji: '💛', value: 'Golden Years' },
        { name: 'Champagne', emoji: '🥂', value: 'Champagne' },
        { name: 'Starry Night', emoji: '⭐', value: 'Starry Night' }
    ],
    'Baby Shower': [
        { name: 'Baby Blue', emoji: '💙', value: 'Baby Blue' },
        { name: 'Soft Pink', emoji: '💗', value: 'Soft Pink' },
        { name: 'Pastel Rainbow', emoji: '🌈', value: 'Pastel Rainbow' },
        { name: 'Teddy Bear', emoji: '🧸', value: 'Teddy Bear' }
    ]
};

document.addEventListener('DOMContentLoaded', () => {
    // State
    let state = {
        eventType: 'Birthday',
        vibe: null,
        details: '',
        userPhotoUrl: null,
        generatedData: null
    };

    // Elements
    const vibeSelector = document.getElementById('vibeSelector');
    const eventDetailsInput = document.getElementById('eventDetails');
    const generateBtn = document.getElementById('generateBtn');
    const resultSection = document.getElementById('resultSection');
    const inputForm = document.getElementById('inputForm');
    const cardTitle = document.getElementById('cardTitle');
    const cardBody = document.getElementById('cardBody');
    const generatedImage = document.getElementById('generatedImage');
    const skeletonLoader = document.getElementById('skeletonLoader');
    const downloadBtn = document.getElementById('downloadBtn');
    const regenerateBtn = document.getElementById('regenerateBtn');

    // Prompt Builder Elements
    const togglePromptBuilder = document.getElementById('togglePromptBuilder');
    const manualInput = document.getElementById('manualInput');
    const promptBuilder = document.getElementById('promptBuilder');
    const generatePromptBtn = document.getElementById('generatePromptBtn');
    const generatedPromptPreview = document.getElementById('generatedPromptPreview');
    const generatedPromptText = document.getElementById('generatedPromptText');
    const copyPromptBtn = document.getElementById('copyPromptBtn');

    // Initialize Uploadcare
    const widget = uploadcare.Widget('[role=uploadcare-uploader]');

    // Custom validator for max size 40MB
    widget.validators.push(function (fileInfo) {
        if (fileInfo.size !== null && fileInfo.size > 40 * 1024 * 1024) {
            throw new Error('File is too large. Maximum size is 40MB.');
        }
    });

    widget.onUploadComplete(info => {
        state.userPhotoUrl = info.cdnUrl;
        console.log('Photo uploaded:', state.userPhotoUrl);
        alert('Photo uploaded successfully!');
    });

    // Initialize Gallery Uploader
    const galleryWidget = uploadcare.Widget('#galleryUploadInput');
    galleryWidget.onUploadComplete(info => {
        // info is a group object when multiple files are uploaded
        if (info.cdnUrl) {
            // For single file or group, cdnUrl is the base
            // If it's a group, we need to fetch the group info or just use the count
            // For simplicity with the demo key, we'll assume a list of URLs if possible
            // But Uploadcare widget returns a group URL for multiple files

            // Let's store the group URL or individual URLs
            // For this demo, we'll just store the group URL and handle it on backend
            // OR better, let's just assume we get a list of CDN URLs if we iterate

            // Actually, for the widget with multiple=true, info.count gives number of files
            // and we can construct URLs: group_url/nth/

            state.galleryPhotos = [];
            if (info.count) {
                for (let i = 0; i < info.count; i++) {
                    state.galleryPhotos.push(`${info.cdnUrl}nth/${i}/`);
                }
            } else {
                state.galleryPhotos.push(info.cdnUrl);
            }
            console.log('Gallery photos:', state.galleryPhotos);
        }
    });

    // Function to render themes based on event type
    function renderThemes(eventType) {
        const themes = EVENT_THEMES[eventType] || EVENT_THEMES['Birthday'];
        vibeSelector.innerHTML = themes.map(theme => `
            <div class="vibe-card" data-vibe="${theme.value}">
                <div class="glass-card rounded-xl p-6 md:p-8 border-2 border-white/20 hover:border-brand-400/50 transition-all duration-300 h-32 md:h-40 flex flex-col justify-center items-center touch-manipulation">
                    <div class="text-3xl md:text-5xl mb-2 md:mb-3">${theme.emoji}</div>
                    <span class="text-xs md:text-sm font-semibold text-white">${theme.name}</span>
                </div>
            </div>
        `).join('');

        // Re-attach click listeners
        attachVibeListeners();

        // Auto-select first theme
        const firstCard = vibeSelector.querySelector('.vibe-card');
        if (firstCard) {
            firstCard.click();
        }
    }

    // Attach vibe selection listeners
    function attachVibeListeners() {
        vibeSelector.querySelectorAll('.vibe-card').forEach(card => {
            card.addEventListener('click', () => {
                // Remove selected class from all
                document.querySelectorAll('.vibe-card').forEach(c => c.classList.remove('selected'));

                // Add to clicked
                card.classList.add('selected');
                state.vibe = card.dataset.vibe;
            });
        });
    }

    // Event type button handlers
    const eventTypeSelector = document.getElementById('eventTypeSelector');
    eventTypeSelector.addEventListener('click', (e) => {
        const btn = e.target.closest('.event-type-btn');
        if (!btn) return;

        // Remove selected from all buttons
        document.querySelectorAll('.event-type-btn').forEach(b => b.classList.remove('selected'));

        // Add selected to clicked button
        btn.classList.add('selected');

        // Update state and render themes
        state.eventType = btn.dataset.event;
        renderThemes(state.eventType);
    });

    // Initialize with Birthday themes
    renderThemes('Birthday');

    // Toggle Prompt Builder
    togglePromptBuilder.addEventListener('click', () => {
        if (manualInput.classList.contains('hidden')) {
            // Switch to manual
            manualInput.classList.remove('hidden');
            promptBuilder.classList.add('hidden');
            togglePromptBuilder.innerHTML = '<i data-lucide="wand-2" class="w-4 h-4"></i> Use Prompt Builder';
            lucide.createIcons();
        } else {
            // Switch to builder
            manualInput.classList.add('hidden');
            promptBuilder.classList.remove('hidden');
            togglePromptBuilder.innerHTML = '<i data-lucide="type" class="w-4 h-4"></i> Write Manually';
            lucide.createIcons();
        }
    });

    // Generate Prompt from Builder
    generatePromptBtn.addEventListener('click', () => {
        const name = document.getElementById('pb_name').value;
        const occasion = document.getElementById('pb_occasion').value;
        const date = document.getElementById('pb_date').value;
        const time = document.getElementById('pb_time').value;
        const venue = document.getElementById('pb_venue').value;
        const additional = document.getElementById('pb_additional').value;

        if (!name || !date || !time || !venue) {
            alert('Please fill in Name, Date, Time, and Venue');
            return;
        }

        // Generate prompt based on event type
        let prompt = '';
        const eventType = state.eventType;

        if (eventType === 'Birthday') {
            prompt = `Join us for ${name}'s ${occasion ? occasion + ' ' : ''}birthday celebration! `;
            prompt += `${date} at ${time} at ${venue}. `;
        } else if (eventType === 'Wedding') {
            prompt = `You're invited to celebrate the wedding of ${name}! `;
            prompt += `Join us on ${date} at ${time} at ${venue}. `;
        } else if (eventType === 'Party') {
            prompt = `You're invited to ${name}'s ${occasion || 'party'}! `;
            prompt += `${date} at ${time} at ${venue}. `;
        } else if (eventType === 'Corporate') {
            prompt = `You're invited to ${occasion || 'our corporate event'} hosted by ${name}. `;
            prompt += `${date} at ${time} at ${venue}. `;
        } else if (eventType === 'Anniversary') {
            prompt = `Celebrate ${name}'s ${occasion || 'anniversary'}! `;
            prompt += `Join us on ${date} at ${time} at ${venue}. `;
        } else if (eventType === 'Baby Shower') {
            prompt = `You're invited to ${name}'s baby shower! `;
            prompt += `${date} at ${time} at ${venue}. `;
        }

        if (additional) {
            prompt += additional;
        }

        // Show generated prompt
        generatedPromptText.value = prompt;
        generatedPromptPreview.classList.remove('hidden');

        // Also update the main event details
        eventDetailsInput.value = prompt;
    });

    // Copy Prompt to Clipboard
    copyPromptBtn.addEventListener('click', () => {
        generatedPromptText.select();
        document.execCommand('copy');
        copyPromptBtn.innerHTML = '<i data-lucide="check" class="w-3 h-3"></i> Copied!';
        lucide.createIcons();
        setTimeout(() => {
            copyPromptBtn.innerHTML = '<i data-lucide="copy" class="w-3 h-3"></i> Copy to Clipboard';
            lucide.createIcons();
        }, 2000);
    });

    // Generate Handler
    generateBtn.addEventListener('click', async () => {
        state.details = eventDetailsInput.value;

        if (!state.details) {
            alert('Please enter event details or use the Prompt Builder!');
            return;
        }

        if (!state.vibe) {
            alert('Please select a theme!');
            return;
        }

        if (!state.userPhotoUrl) {
            alert('Please upload a photo to continue!');
            return;
        }

        const eventLocation = document.getElementById('eventLocationInput').value;
        if (!eventLocation) {
            alert('Please enter the event location!');
            return;
        }

        setButtonLoading(generateBtn, true);

        try {
            // Step 1: Refine Prompt (Gemini)
            const refineResponse = await fetch('/api/refine-prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    eventType: state.eventType,
                    vibe: state.vibe,
                    details: state.details
                })
            });

            if (refineResponse.status === 401) {
                alert('Please login to generate invitations!');
                window.location.href = '/login';
                return;
            }

            const refineResult = await refineResponse.json();
            if (!refineResult.success) throw new Error(refineResult.error);

            state.generatedData = refineResult.data;

            // Show Text Immediately
            inputForm.classList.add('hidden');
            resultSection.classList.remove('hidden');
            resultSection.classList.add('fade-in');

            cardTitle.textContent = state.generatedData.card_title;
            cardBody.textContent = state.generatedData.card_body;

            // Reset Image State
            generatedImage.style.display = 'none';
            skeletonLoader.style.display = 'block';

            // Step 2: Generate Image
            const imageResponse = await fetch('/api/generate-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_prompt: state.generatedData.image_prompt,
                    user_photo_url: state.userPhotoUrl,
                    gallery_photos: state.galleryPhotos, // Send gallery photos
                    location_name: eventLocation, // Send location
                    title: state.generatedData.card_title,
                    body: state.generatedData.card_body,
                    eventType: state.eventType,
                    vibe: state.vibe
                })
            });

            if (imageResponse.status === 401) {
                alert('Session expired. Please login again!');
                window.location.href = '/login';
                return;
            }

            const imageResult = await imageResponse.json();
            if (!imageResult.success) throw new Error(imageResult.error);

            // Store invitation data for sharing
            if (imageResult.invitation_id) {
                state.invitationId = imageResult.invitation_id;
                state.shareLink = imageResult.share_link;
                console.log('Invitation created with share link:', state.shareLink);
            }

            // Show Image
            generatedImage.src = imageResult.image_url;
            generatedImage.onload = () => {
                skeletonLoader.style.display = 'none';
                generatedImage.style.display = 'block';
                generatedImage.classList.add('fade-in');

                // Show User Photo Overlay if available
                const userPhotoContainer = document.getElementById('userPhotoContainer');
                const userPhotoOverlay = document.getElementById('userPhotoOverlay');

                if (state.userPhotoUrl) {
                    userPhotoOverlay.src = state.userPhotoUrl;
                    userPhotoContainer.classList.remove('hidden');
                } else {
                    userPhotoContainer.classList.add('hidden');
                }

                // Show share link if available
                if (state.shareLink) {
                    showShareLink(state.shareLink);
                }
            };

        } catch (error) {
            console.error('Error:', error);
            alert('Something went wrong: ' + error.message);
            inputForm.classList.remove('hidden');
            resultSection.classList.add('hidden');
        } finally {
            setButtonLoading(generateBtn, false);
        }
    });

    // Regenerate Handler
    regenerateBtn.addEventListener('click', () => {
        resultSection.classList.add('hidden');
        inputForm.classList.remove('hidden');
        inputForm.classList.add('fade-in');
    });

    // Download Handler
    downloadBtn.addEventListener('click', async () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        canvas.width = 1920;
        canvas.height = 1080;

        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = generatedImage.src;

        await new Promise(resolve => {
            img.onload = resolve;
            if (img.complete) resolve();
        });

        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

        // Add Overlay
        const gradient = ctx.createLinearGradient(0, canvas.height / 2, 0, canvas.height);
        gradient.addColorStop(0, 'rgba(0,0,0,0)');
        gradient.addColorStop(1, 'rgba(0,0,0,0.8)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw Text
        ctx.textAlign = 'center';
        ctx.fillStyle = 'white';

        ctx.font = 'bold 80px Inter, sans-serif';
        ctx.shadowColor = "rgba(0,0,0,0.8)";
        ctx.shadowBlur = 20;
        ctx.fillText(cardTitle.textContent, canvas.width / 2, canvas.height - 300);

        ctx.font = '40px Inter, sans-serif';
        wrapText(ctx, cardBody.textContent, canvas.width / 2, canvas.height - 200, 1400, 50);

        const link = document.createElement('a');
        link.download = 'phovite-invitation.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    });

    // Utility: Button Loading
    function setButtonLoading(btn, isLoading) {
        if (isLoading) {
            btn.classList.add('btn-loading');
            btn.disabled = true;
        } else {
            btn.classList.remove('btn-loading');
            btn.disabled = false;
        }
    }

    // Utility: Wrap Text for Canvas
    function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
        const words = text.split(' ');
        let line = '';

        for (let n = 0; n < words.length; n++) {
            const testLine = line + words[n] + ' ';
            const metrics = ctx.measureText(testLine);
            const testWidth = metrics.width;
            if (testWidth > maxWidth && n > 0) {
                ctx.fillText(line, x, y);
                line = words[n] + ' ';
                y += lineHeight;
            } else {
                line = testLine;
            }
        }
        ctx.fillText(line, x, y);
    }

    // Show Share Link Function
    function showShareLink(shareLink) {
        const shareUrl = `${window.location.origin}/invite/${shareLink}`;
        const publicLinkBtn = document.getElementById('publicLinkBtn');
        if (publicLinkBtn) {
            publicLinkBtn.href = shareUrl;
        }

        // Reinitialize Lucide icons
        lucide.createIcons();
        console.log('Share your invitation:', shareUrl);
    }

    // --- NEW FEATURES LOGIC ---

    // 1. Live Editor
    window.toggleEditMode = function () {
        const isEditing = cardTitle.isContentEditable;
        cardTitle.contentEditable = !isEditing;
        cardBody.contentEditable = !isEditing;

        const styleControls = document.getElementById('styleControls');
        const editBtn = document.querySelector('#liveEditorControls button'); // The first button

        if (!isEditing) {
            // Enter Edit Mode
            cardTitle.focus();
            styleControls.classList.remove('hidden');
            styleControls.classList.add('flex');

            editBtn.innerHTML = '<i data-lucide="check" class="w-4 h-4"></i> Done';
            editBtn.classList.remove('bg-black/50', 'hover:bg-black/70');
            editBtn.classList.add('bg-green-500/50', 'hover:bg-green-500/70');
        } else {
            // Exit Edit Mode
            styleControls.classList.add('hidden');
            styleControls.classList.remove('flex');

            editBtn.innerHTML = '<i data-lucide="edit-3" class="w-4 h-4"></i> Edit Text';
            editBtn.classList.add('bg-black/50', 'hover:bg-black/70');
            editBtn.classList.remove('bg-green-500/50', 'hover:bg-green-500/70');

            // Save changes (optional: call API to update title/body)
        }
        lucide.createIcons();
    };

    window.changeFont = function (fontClass) {
        // Remove existing font classes
        cardTitle.classList.remove('font-display', 'font-serif', 'font-mono');
        cardBody.classList.remove('font-display', 'font-serif', 'font-mono');

        // Add new font class
        cardTitle.classList.add(fontClass);
        cardBody.classList.add(fontClass);
    };

    window.changeColor = function (colorClass) {
        // Remove existing color classes
        const colors = ['text-white', 'text-black', 'text-yellow-400', 'text-gray-100', 'text-gray-900'];
        cardTitle.classList.remove(...colors);
        cardBody.classList.remove(...colors);

        // Add new color class
        cardTitle.classList.add(colorClass);
        cardBody.classList.add(colorClass);
    };

    // 2. Video Generation
    const generateVideoBtn = document.getElementById('generateVideoBtn');
    if (generateVideoBtn) {
        generateVideoBtn.addEventListener('click', async () => {
            console.log('Generating video for invitation ID:', state.invitationId);
            if (!state.invitationId) {
                alert('Error: Invitation ID not found. Please regenerate the invitation.');
                return;
            }

            const originalText = generateVideoBtn.innerHTML;
            generateVideoBtn.disabled = true;

            // Simulated Progress Loader
            let progress = 0;
            generateVideoBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Generating 0%`;
            lucide.createIcons();

            const progressInterval = setInterval(() => {
                if (progress < 90) {
                    progress += Math.floor(Math.random() * 5) + 1; // Random increment
                    if (progress > 90) progress = 90;
                    generateVideoBtn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> Generating ${progress}%`;
                    lucide.createIcons();
                }
            }, 500); // Update every 500ms

            try {
                const response = await fetch('/api/generate-video', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ invitation_id: state.invitationId })
                });

                // Clear interval and set to 100%
                clearInterval(progressInterval);
                generateVideoBtn.innerHTML = `<i data-lucide="check" class="w-4 h-4"></i> Generating 100%`;
                lucide.createIcons();

                const result = await response.json();

                if (result.success) {
                    // Small delay to let user see 100%
                    setTimeout(() => {
                        alert('Video generated! Downloading now...');
                        console.log('Video URL:', result.video_url);

                        // Automatic Download
                        const link = document.createElement('a');
                        link.href = result.video_url;
                        link.download = 'phovite_hype_story.mp4';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);

                        // Reset button
                        generateVideoBtn.innerHTML = originalText;
                        generateVideoBtn.disabled = false;
                        lucide.createIcons();
                    }, 500);

                } else {
                    alert('Error: ' + result.error);
                    generateVideoBtn.innerHTML = originalText;
                    generateVideoBtn.disabled = false;
                    lucide.createIcons();
                }
            } catch (e) {
                clearInterval(progressInterval);
                console.error(e);
                alert('Failed to generate video');
                generateVideoBtn.innerHTML = originalText;
                generateVideoBtn.disabled = false;
                lucide.createIcons();
            }
        });
    }

    // 3. RSVP Handling (Public Page)
    const rsvpForm = document.getElementById('rsvpForm');
    if (rsvpForm) {
        rsvpForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = rsvpForm.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="loader-2" class="w-5 h-5 animate-spin"></i> Processing...';
            btn.disabled = true;
            lucide.createIcons();

            try {
                const formData = new FormData(rsvpForm);
                // Add invitation ID from URL or template context
                // For now assuming we are on the invite page and can get ID from context or URL
                // In a real implementation, we'd pass invitation.id to a data attribute

                // Mock success for now since we don't have the full backend wired for file upload in this snippet
                // const response = await fetch('/api/rsvp', { method: 'POST', body: formData });

                // Simulate delay
                await new Promise(r => setTimeout(r, 1500));

                document.getElementById('rsvpSuccess').classList.remove('hidden');
                rsvpForm.classList.add('hidden');

                // Show confetti
                // confetti(); 

            } catch (e) {
                console.error(e);
                alert('RSVP failed');
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
                lucide.createIcons();
            }
        });
    }

});
