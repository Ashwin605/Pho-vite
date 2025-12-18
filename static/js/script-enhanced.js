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
        familyName: '',
        celebrantName: '',
        eventDate: '',
        eventTime: '',
        eventVenue: '',
        eventMessage: '',
        userPhotoUrl: null,
        generatedData: null,
        selectedMusic: null,
        voiceMessageUrl: null
    };

    // Elements
    const vibeSelector = document.getElementById('vibeSelector');
    const generateBtn = document.getElementById('generateBtn');
    const resultSection = document.getElementById('resultSection');
    const inputForm = document.getElementById('inputForm');
    const cardTitle = document.getElementById('cardTitle');
    const cardBody = document.getElementById('cardBody');
    const generatedImage = document.getElementById('generatedImage');
    const skeletonLoader = document.getElementById('skeletonLoader');
    const regenerateBtn = document.getElementById('regenerateBtn');

    // Function to render themes based on event type
    function renderThemes(eventType) {
        const themes = EVENT_THEMES[eventType] || EVENT_THEMES['Birthday'];
        vibeSelector.innerHTML = themes.map(theme => `
            <div class="vibe-card" data-vibe="${theme.value}">
                <div class="glass-card rounded-xl p-6 md:p-8 border-2 border-transparent hover:border-orange-500 transition-all duration-300 h-32 md:h-40 flex flex-col justify-center items-center touch-manipulation cursor-pointer shadow-sm bg-white">
                    <div class="text-3xl md:text-5xl mb-2 md:mb-3">${theme.emoji}</div>
                    <span class="text-xs md:text-sm font-semibold text-navy-900">${theme.name}</span>
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

        // Update dynamic fields based on event type
        updateDynamicFields(state.eventType);
    });

    // Function to show/hide dynamic fields based on event type
    function updateDynamicFields(eventType) {
        // Hide all event-specific field groups
        document.getElementById('birthdayFields').classList.add('hidden');
        document.getElementById('weddingFields').classList.add('hidden');
        document.getElementById('anniversaryFields').classList.add('hidden');
        document.getElementById('babyShowerFields').classList.add('hidden');
        document.getElementById('corporateFields').classList.add('hidden');
        document.getElementById('partyFields').classList.add('hidden');

        // Show the relevant fields based on event type
        switch (eventType) {
            case 'Birthday':
                document.getElementById('birthdayFields').classList.remove('hidden');
                break;
            case 'Wedding':
                document.getElementById('weddingFields').classList.remove('hidden');
                break;
            case 'Anniversary':
                document.getElementById('anniversaryFields').classList.remove('hidden');
                break;
            case 'Baby Shower':
                document.getElementById('babyShowerFields').classList.remove('hidden');
                break;
            case 'Corporate':
                document.getElementById('corporateFields').classList.remove('hidden');
                break;
            case 'Party':
                document.getElementById('partyFields').classList.remove('hidden');
                break;
        }
    }

    // Initialize with Birthday themes and fields
    renderThemes('Birthday');
    updateDynamicFields('Birthday');

    // Helper function to convert file to base64
    async function fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    // Generate Handler
    generateBtn.addEventListener('click', async () => {
        // Get common input values
        state.familyName = document.getElementById('familyName').value.trim();
        state.eventDate = document.getElementById('eventDate').value.trim();
        state.eventTime = document.getElementById('eventTime').value.trim();
        state.eventVenue = document.getElementById('eventVenue').value.trim();
        state.eventMessage = document.getElementById('eventMessage').value.trim();

        // Event-specific data collection and validation
        let eventSpecificData = {};

        switch (state.eventType) {
            case 'Birthday':
                state.celebrantName = document.getElementById('celebrantName').value.trim();
                const celebrantPhotoFile = document.getElementById('celebrantPhoto').files[0];

                if (!state.celebrantName) {
                    alert('Please enter the birthday person\'s name!');
                    return;
                }
                if (!celebrantPhotoFile) {
                    alert('Please upload a photo of the birthday person!');
                    return;
                }

                eventSpecificData.celebrantName = state.celebrantName;
                eventSpecificData.celebrantPhoto = await fileToBase64(celebrantPhotoFile);
                // Store photo URL for display in overlay
                state.userPhotoUrl = eventSpecificData.celebrantPhoto;
                console.log('Birthday photo stored:', state.userPhotoUrl ? state.userPhotoUrl.substring(0, 50) + '...' : null);
                break;

            case 'Wedding':
                const brideName = document.getElementById('brideName').value.trim();
                const groomName = document.getElementById('groomName').value.trim();
                const bridePhotoFile = document.getElementById('bridePhoto').files[0];
                const groomPhotoFile = document.getElementById('groomPhoto').files[0];

                if (!brideName) {
                    alert('Please enter the bride\'s name!');
                    return;
                }
                if (!groomName) {
                    alert('Please enter the groom\'s name!');
                    return;
                }
                if (!bridePhotoFile) {
                    alert('Please upload the bride\'s photo!');
                    return;
                }
                if (!groomPhotoFile) {
                    alert('Please upload the groom\'s photo!');
                    return;
                }

                eventSpecificData.brideName = brideName;
                eventSpecificData.groomName = groomName;
                eventSpecificData.bridePhoto = await fileToBase64(bridePhotoFile);
                eventSpecificData.groomPhoto = await fileToBase64(groomPhotoFile);
                // Store photos for display in overlay
                state.userPhotoUrl = eventSpecificData.bridePhoto;
                state.secondaryPhotoUrl = eventSpecificData.groomPhoto;
                state.celebrantName = `${brideName} & ${groomName}`;
                break;

            case 'Anniversary':
                const coupleNames = document.getElementById('coupleNames').value.trim();
                const couplePhotoFile = document.getElementById('couplePhoto').files[0];

                if (!coupleNames) {
                    alert('Please enter the couple\'s names!');
                    return;
                }

                eventSpecificData.coupleNames = coupleNames;
                if (couplePhotoFile) {
                    eventSpecificData.couplePhoto = await fileToBase64(couplePhotoFile);
                    // Store photo for display in overlay
                    state.userPhotoUrl = eventSpecificData.couplePhoto;
                }
                state.celebrantName = coupleNames;
                break;

            case 'Baby Shower':
                const babyName = document.getElementById('babyName').value.trim() || 'Little One';
                const babyGender = document.getElementById('babyGender').value;

                eventSpecificData.babyName = babyName;
                eventSpecificData.babyGender = babyGender;
                state.celebrantName = babyName;
                break;

            case 'Corporate':
                const companyName = document.getElementById('companyName').value.trim();
                const corporateEventName = document.getElementById('corporateEventName').value.trim();

                if (!companyName) {
                    alert('Please enter the company name!');
                    return;
                }
                if (!corporateEventName) {
                    alert('Please enter the event name!');
                    return;
                }

                eventSpecificData.companyName = companyName;
                eventSpecificData.corporateEventName = corporateEventName;
                state.celebrantName = corporateEventName;
                break;

            case 'Party':
                const partyName = document.getElementById('partyName').value.trim();

                if (!partyName) {
                    alert('Please enter the event name!');
                    return;
                }

                eventSpecificData.partyName = partyName;
                state.celebrantName = partyName;
                break;
        }

        // Common validation
        if (!state.eventDate) {
            alert('Please enter the event date!');
            return;
        }

        if (!state.eventTime) {
            alert('Please enter the event time!');
            return;
        }

        if (!state.eventVenue) {
            alert('Please enter the event venue!');
            return;
        }

        if (!state.vibe) {
            alert('Please select a theme!');
            return;
        }

        setButtonLoading(generateBtn, true);

        // Show progress indicator
        showProgressIndicator();

        // Small delay to ensure DOM is updated
        await new Promise(resolve => setTimeout(resolve, 150));
        updateProgressStep(1, 'active');

        try {
            // Build detailed welcoming prompt
            let details = '';
            if (state.eventType === 'Wedding' && eventSpecificData.brideName && eventSpecificData.groomName) {
                details = `With joyous hearts, the ${state.familyName || 'family'} invites you to celebrate the sacred union of ${eventSpecificData.brideName} and ${eventSpecificData.groomName}. Please join us on ${state.eventDate} at ${state.eventTime} at ${state.eventVenue}. ${state.eventMessage || 'as their beautiful love story begins.'}`;
            } else {
                details = `With joyous hearts, we invite you to celebrate ${state.celebrantName}'s special ${state.eventType}! Please join us on ${state.eventDate} at ${state.eventTime} at ${state.eventVenue}. ${state.eventMessage}`;
            }

            // Step 1: Refine Prompt (Background)
            const refineResponse = await fetch('/api/refine-prompt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    eventType: state.eventType,
                    vibe: state.vibe,
                    details: details,
                    familyName: state.familyName,
                    celebrantName: state.celebrantName
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

            // Step 2: Generate Image (Background)
            const imageResponse = await fetch('/api/generate-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_prompt: state.generatedData.image_prompt,
                    user_photo_url: state.userPhotoUrl,
                    title: state.generatedData.card_title,
                    body: state.generatedData.card_body,
                    story: state.generatedData.story,
                    eventType: state.eventType,
                    vibe: state.vibe,
                    familyName: state.familyName,
                    celebrantName: state.celebrantName,
                    eventDate: state.eventDate,
                    eventTime: state.eventTime,
                    eventVenue: state.eventVenue,
                    eventMessage: state.eventMessage,
                    location_name: state.eventVenue,
                    ...eventSpecificData
                })
            });

            const imageResult = await imageResponse.json();
            if (!imageResult.success) throw new Error(imageResult.error);

            // Store invitation data
            if (imageResult.invitation_id) {
                state.invitation_id = imageResult.invitation_id;
                state.share_link = imageResult.share_link;
            }

            // Hide progress and display results with animation
            hideProgressIndicator();
            displayResults(imageResult.image_url, true); // true for animate

        } catch (error) {
            console.error('Generation error:', error);
            hideProgressIndicator();
            alert(`Error: ${error.message}`);
        } finally {
            setButtonLoading(generateBtn, false);
        }
    });

    function displayResults(imageUrl, animate = false) {
        // Show result section
        resultSection.classList.remove('hidden');

        // Set background image with error handling
        generatedImage.onerror = function () {
            console.log('Image failed to load, using gradient fallback');
            // Set a beautiful gradient fallback
            this.style.display = 'none';
            const imageContainer = this.parentElement;
            if (imageContainer) {
                imageContainer.style.background = 'linear-gradient(135deg, #1a0033 0%, #2d0050 25%, #4a0080 50%, #2d0050 75%, #1a0033 100%)';
            }
        };

        generatedImage.onload = function () {
            console.log('Image loaded successfully');
            this.style.display = 'block';
            skeletonLoader.style.display = 'none';
        };

        generatedImage.src = imageUrl;
        skeletonLoader.style.display = 'none';

        // Elements to animate
        const elements = [
            document.getElementById('familyNameText'),
            cardTitle,
            document.getElementById('dateText'),
            document.getElementById('timeText'),
            document.getElementById('venueText'),
            cardBody
        ];

        // Reset opacity if animating
        if (animate) {
            elements.forEach(el => {
                if (el) {
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(20px)';
                    el.style.transition = 'all 0.5s ease-out';
                }
            });
        }

        // Update Content
        const familyNameText = document.getElementById('familyNameText');
        if (familyNameText) familyNameText.textContent = state.familyName;

        if (cardTitle) cardTitle.textContent = state.celebrantName;

        const dateText = document.getElementById('dateText');
        const timeText = document.getElementById('timeText');
        const venueText = document.getElementById('venueText');

        if (dateText) dateText.textContent = state.eventDate;
        if (timeText) timeText.textContent = state.eventTime;
        if (venueText) venueText.textContent = state.eventVenue;

        if (cardBody && state.eventMessage) {
            cardBody.textContent = state.eventMessage;
        } else if (cardBody) {
            cardBody.textContent = state.generatedData?.card_body || 'Join us for this special celebration!';
        }

        // Setup public link
        if (state.share_link) {
            const publicLinkBtn = document.getElementById('publicLinkBtn');
            if (publicLinkBtn) {
                publicLinkBtn.href = `/invite/${state.share_link}`;
            }
        }

        // Store invitation_id globally
        if (state.invitation_id) {
            window.currentInvitationId = state.invitation_id;
            resultSection.dataset.invitationId = state.invitation_id;
        }

        // Display user photo overlay if available
        const userPhotoContainer = document.getElementById('userPhotoContainer');
        const userPhotoOverlay = document.getElementById('userPhotoOverlay');

        console.log('Photo display check:', {
            hasContainer: !!userPhotoContainer,
            hasOverlay: !!userPhotoOverlay,
            hasPhotoUrl: !!state.userPhotoUrl,
            photoUrl: state.userPhotoUrl ? state.userPhotoUrl.substring(0, 50) + '...' : null
        });

        if (userPhotoContainer && userPhotoOverlay && state.userPhotoUrl) {
            console.log('Displaying user photo in overlay');
            userPhotoOverlay.src = state.userPhotoUrl;
            userPhotoContainer.classList.remove('hidden');
            userPhotoContainer.style.display = 'block'; // Force display

            // Add animation
            if (animate) {
                userPhotoContainer.style.opacity = '0';
                userPhotoContainer.style.transform = 'scale(0.5)';
                userPhotoContainer.style.transition = 'all 0.6s ease-out';

                setTimeout(() => {
                    userPhotoContainer.style.opacity = '1';
                    userPhotoContainer.style.transform = 'scale(1)';
                }, 200);
            } else {
                userPhotoContainer.style.opacity = '1';
                userPhotoContainer.style.transform = 'scale(1)';
            }
        } else {
            console.log('Photo not displayed - missing requirements');
        }

        // Reinitialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Scroll to results
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // Animate elements one by one
        if (animate) {
            elements.forEach((el, index) => {
                if (el) {
                    setTimeout(() => {
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    }, 300 + (index * 200));
                }
            });
        }
    }



    // Audio Preview Logic
    // Audio Preview Function (Renamed to bypass cache)
    window.playMusicPreview = function (musicKey, btn) {
        // Stop event propagation to prevent selection
        event.stopPropagation();

        const musicMap = {
            'happy_birthday': 'happy_birthday.mp3',
            'wedding_bells': 'wedding_bells.mp3',
            'party_time': 'party_time.mp3',
            'celebration': 'celebration.mp3',
            'elegant_classic': 'elegant_classic.mp3',
            'upbeat_pop': 'upbeat_pop.mp3'
        };

        const audio = document.getElementById('musicPreviewPlayer');
        const icon = btn.querySelector('i') || btn.querySelector('svg');

        // If already playing this track, pause it
        if (!audio.paused && audio.dataset.currentTrack === musicKey) {
            audio.pause();
            icon.setAttribute('data-lucide', 'play');
            lucide.createIcons();
            return;
        }

        // Reset all buttons
        document.querySelectorAll('.music-option-container button i').forEach(i => {
            if (i.parentElement.classList.contains('absolute')) {
                i.setAttribute('data-lucide', 'play');
            }
        });

        // Play new track
        const filename = musicMap[musicKey];
        if (filename) {
            audio.src = `/static/audio/${filename}`;
            audio.dataset.currentTrack = musicKey;
            audio.play().catch(e => {
                console.log("Audio play failed (likely no file):", e);
                alert("Preview not available for this track yet.");
            });

            icon.setAttribute('data-lucide', 'pause');
            lucide.createIcons();

            audio.onended = () => {
                icon.setAttribute('data-lucide', 'play');
                lucide.createIcons();
            };
        }
    };

    // Gallery Upload Logic
    const galleryUpload = document.getElementById('galleryUpload');
    if (galleryUpload) {
        galleryUpload.addEventListener('change', async (e) => {
            const files = e.target.files;
            if (!files.length) return;

            const invitationId = state.invitation_id || window.currentInvitationId;
            if (!invitationId) {
                alert("Please generate an invitation first!");
                return;
            }

            const formData = new FormData();
            formData.append('invitation_id', invitationId);
            for (let i = 0; i < files.length; i++) {
                formData.append('photos', files[i]);
            }

            try {
                const btn = galleryUpload.nextElementSibling;
                const originalContent = btn.innerHTML;
                btn.innerHTML = '<div class="spinner-border spinner-border-sm"></div> Uploading...';

                const response = await fetch('/api/upload-gallery', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                if (result.success) {
                    // Update preview
                    const previewDiv = document.getElementById('galleryPreview');
                    result.photos.forEach(url => {
                        const img = document.createElement('img');
                        img.src = url;
                        img.className = 'w-full h-20 object-cover rounded-lg border border-white/20';
                        previewDiv.appendChild(img);
                    });
                    alert("Photos added to gallery!");
                } else {
                    alert("Upload failed: " + result.error);
                }

                btn.innerHTML = originalContent;
            } catch (error) {
                console.error("Gallery upload error:", error);
                alert("Upload failed");
            }
        });
    }

    // Video Generation with Music Selection
    const generateVideoBtn = document.getElementById('generateVideoBtn');
    if (generateVideoBtn) {
        generateVideoBtn.addEventListener('click', async () => {
            // Check both state and global variable
            let invitationId = state.invitation_id || window.currentInvitationId || resultSection?.dataset?.invitationId;

            // If still not found, try to get it from the share link
            if (!invitationId) {
                const publicLinkBtn = document.getElementById('publicLinkBtn');
                if (publicLinkBtn && publicLinkBtn.href) {
                    const shareLink = publicLinkBtn.href.split('/invite/')[1];
                    if (shareLink) {
                        console.log('Fetching invitation ID from share link:', shareLink);
                        try {
                            const response = await fetch(`/api/get-invitation-id-by-link/${shareLink}`);
                            const result = await response.json();
                            if (result.success) {
                                invitationId = result.invitation_id;
                                state.invitation_id = invitationId;
                                window.currentInvitationId = invitationId;
                                console.log('Retrieved invitation ID:', invitationId);
                            }
                        } catch (error) {
                            console.error('Error fetching invitation ID:', error);
                        }
                    }
                }
            }

            if (!invitationId) {
                alert('Please generate an invitation first!');
                return;
            }

            // Store in state if found in global/dataset
            if (!state.invitation_id && invitationId) {
                state.invitation_id = invitationId;
                window.currentInvitationId = invitationId;
            }

            console.log('Starting video generation for invitation:', invitationId);

            // Show music modal
            openMusicModal();
        });
    }

    // Regenerate button
    if (regenerateBtn) {
        regenerateBtn.addEventListener('click', () => {
            resultSection.classList.add('hidden');
            inputForm.scrollIntoView({ behavior: 'smooth' });

            // Reset state
            state.generatedData = null;
            state.invitation_id = null;
            state.share_link = null;
        });
    }

    // Helper functions
    function setButtonLoading(button, loading) {
        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<div class="spinner-border spinner-border-sm"></div> Generating...';
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.disabled = false;
        }
    }

    // Progress indicator functions
    function showProgressIndicator() {
        const progressDiv = document.getElementById('progressIndicator');
        if (progressDiv) {
            // Reset all steps first
            resetProgressSteps();
            progressDiv.classList.remove('hidden');
            // Scroll to it
            setTimeout(() => {
                progressDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
    }

    function hideProgressIndicator() {
        const progressDiv = document.getElementById('progressIndicator');
        if (progressDiv) {
            progressDiv.classList.add('hidden');
        }
    }

    function resetProgressSteps() {
        // Reset all steps to initial state
        const steps = document.querySelectorAll('.progress-step');
        steps.forEach(step => {
            const icon = step.querySelector('.step-icon');
            const statusIcon = step.querySelector('.step-status');
            if (icon) {
                icon.classList.remove('bg-purple-500', 'bg-green-500', 'animate-pulse');
                icon.classList.add('bg-slate-700');
                const iconElement = icon.querySelector('i') || icon.querySelector('svg');
                if (iconElement) {
                    iconElement.classList.remove('text-white');
                    iconElement.classList.add('text-gray-400');
                }
            }
            if (statusIcon) {
                statusIcon.classList.add('hidden');
            }
        });

        // Reset progress bar
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = '0%';
        }
    }

    function updateProgressStep(stepNumber, status) {
        const step = document.querySelector(`.progress-step[data-step="${stepNumber}"]`);
        if (!step) return;

        const icon = step.querySelector('.step-icon');
        const statusIcon = step.querySelector('.step-status');
        const progressBar = document.getElementById('progressBar');

        // Add null checks to prevent errors
        if (!icon) return;

        if (status === 'active') {
            // Highlight current step
            icon.classList.remove('bg-slate-700');
            icon.classList.add('bg-purple-500', 'animate-pulse');
            // Try both i and svg (Lucide converts i to svg)
            const iconElement = icon.querySelector('i') || icon.querySelector('svg');
            if (iconElement) {
                iconElement.classList.remove('text-gray-400');
                iconElement.classList.add('text-white');
            }
        } else if (status === 'completed') {
            // Mark as completed
            icon.classList.remove('animate-pulse', 'bg-purple-500', 'bg-slate-700');
            icon.classList.add('bg-green-500');
            if (statusIcon) {
                statusIcon.classList.remove('hidden');
            }

            // Update progress bar
            if (progressBar) {
                const progress = (stepNumber / 4) * 100;
                progressBar.style.width = `${progress}%`;
            }

            // Re-initialize lucide icons
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
    }
    // --- AUDIO STUDIO LOGIC ---
    const tabUpload = document.getElementById('tabUpload');
    const tabRecord = document.getElementById('tabRecord');
    const uploadSection = document.getElementById('uploadSection');
    const recordSection = document.getElementById('recordSection');
    const audioUpload = document.getElementById('audioUpload');
    const recordBtn = document.getElementById('recordBtn');
    const recordTimer = document.getElementById('recordTimer');
    const recordStatus = document.getElementById('recordStatus');
    const audioPreview = document.getElementById('audioPreview');
    const playPauseBtn = document.getElementById('playPauseBtn');
    const audioProgress = document.getElementById('audioProgress');
    const audioElement = document.getElementById('audioElement');
    const deleteAudioBtn = document.getElementById('deleteAudioBtn');
    const micVisualizer = document.getElementById('micVisualizer');

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordingStartTime;
    let timerInterval;
    let audioBlob;

    // Tab Switching
    if (tabUpload && tabRecord) {
        tabUpload.addEventListener('click', () => {
            tabUpload.classList.add('bg-white/10', 'text-white');
            tabUpload.classList.remove('bg-transparent', 'text-gray-400');
            tabRecord.classList.remove('bg-white/10', 'text-white');
            tabRecord.classList.add('bg-transparent', 'text-gray-400');

            uploadSection.classList.remove('hidden');
            recordSection.classList.add('hidden');
        });

        tabRecord.addEventListener('click', () => {
            tabRecord.classList.add('bg-white/10', 'text-white');
            tabRecord.classList.remove('bg-transparent', 'text-gray-400');
            tabUpload.classList.remove('bg-white/10', 'text-white');
            tabUpload.classList.add('bg-transparent', 'text-gray-400');

            recordSection.classList.remove('hidden');
            uploadSection.classList.add('hidden');
        });
    }

    // File Upload
    if (audioUpload) {
        audioUpload.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            if (file.size > 10 * 1024 * 1024) { // 10MB limit
                alert('File is too large. Max 10MB.');
                return;
            }

            // Upload directly
            await uploadAudioFile(file);
        });
    }

    // Recording Logic
    if (recordBtn) {
        recordBtn.addEventListener('click', async () => {
            if (!isRecording) {
                // Start Recording
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];

                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };

                    mediaRecorder.onstop = async () => {
                        audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
                        // Create file from blob
                        const file = new File([audioBlob], "recording.mp3", { type: "audio/mp3" });
                        await uploadAudioFile(file);

                        // Reset UI
                        recordBtn.classList.remove('animate-pulse', 'bg-slate-700');
                        recordBtn.classList.add('bg-red-500', 'hover:bg-red-600');
                        recordBtn.innerHTML = '<i data-lucide="mic" class="w-8 h-8 text-white"></i>';
                        micVisualizer.classList.add('opacity-50');
                        recordStatus.textContent = "Tap to record (max 15s)";
                        clearInterval(timerInterval);
                        recordTimer.textContent = "00:00";
                        lucide.createIcons();
                    };

                    // Audio Context for Visualizer
                    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    const analyser = audioContext.createAnalyser();
                    const source = audioContext.createMediaStreamSource(stream);
                    source.connect(analyser);
                    analyser.fftSize = 32;
                    const bufferLength = analyser.frequencyBinCount;
                    const dataArray = new Uint8Array(bufferLength);

                    const visualizerBars = micVisualizer.querySelectorAll('div');

                    function animateVisualizer() {
                        if (!isRecording) return;
                        requestAnimationFrame(animateVisualizer);
                        analyser.getByteFrequencyData(dataArray);

                        // Simple visualization: Map frequency data to bar heights
                        // We have 3 bars, let's pick 3 frequencies
                        const val1 = dataArray[2] / 255;
                        const val2 = dataArray[4] / 255;
                        const val3 = dataArray[6] / 255;

                        visualizerBars[0].style.height = `${8 + (val1 * 24)}px`;
                        visualizerBars[1].style.height = `${16 + (val2 * 32)}px`;
                        visualizerBars[2].style.height = `${8 + (val3 * 24)}px`;
                    }
                    animateVisualizer();

                    mediaRecorder.start();
                    isRecording = true;
                    recordingStartTime = Date.now();

                    // UI Updates
                    recordBtn.classList.remove('bg-red-500', 'hover:bg-red-600');
                    recordBtn.classList.add('bg-slate-700', 'animate-pulse');
                    recordBtn.innerHTML = '<i data-lucide="square" class="w-6 h-6 text-white"></i>';
                    micVisualizer.classList.remove('opacity-50');
                    recordStatus.textContent = "Recording... Tap to stop";
                    lucide.createIcons();

                    // Timer
                    timerInterval = setInterval(() => {
                        const elapsed = Date.now() - recordingStartTime;
                        const seconds = Math.floor(elapsed / 1000);
                        const ms = Math.floor((elapsed % 1000) / 10);
                        recordTimer.textContent = `00:${seconds.toString().padStart(2, '0')}`;

                        // Auto stop after 15s
                        if (seconds >= 15) {
                            stopRecording();
                        }
                    }, 100);

                } catch (err) {
                    console.error("Error accessing microphone:", err);
                    alert("Could not access microphone. Please allow permissions.");
                }
            } else {
                stopRecording();
            }
        });
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            // Stop all tracks
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }

    async function uploadAudioFile(file) {
        // Show loading state
        if (tabUpload) {
            const originalText = tabUpload.textContent; // Just a placeholder for loading indication
        }

        const formData = new FormData();
        formData.append('voice', file);

        try {
            const response = await fetch('/api/upload-voice', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (result.success) {
                state.voiceMessageUrl = result.voice_url;

                // Setup Preview
                if (audioElement && audioPreview) {
                    audioElement.src = state.voiceMessageUrl;
                    audioPreview.classList.remove('hidden');
                }

                // Auto-save to invitation if ID exists
                if (state.invitationId || window.currentInvitationId) {
                    await saveVoiceToInvitation(state.invitationId || window.currentInvitationId, state.voiceMessageUrl);
                }

                alert('Audio added successfully!');
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload audio: ' + error.message);
        }
    }

    async function saveVoiceToInvitation(invitationId, voiceUrl) {
        try {
            await fetch('/api/enhance-invitation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    invitation_id: invitationId,
                    voice_message_url: voiceUrl
                })
            });
            console.log('Voice saved to invitation');
        } catch (e) {
            console.error('Failed to save voice to invitation:', e);
        }
    }

    // Audio Player Logic
    if (playPauseBtn && audioElement) {
        playPauseBtn.addEventListener('click', () => {
            if (audioElement.paused) {
                audioElement.play();
                playPauseBtn.innerHTML = '<i data-lucide="pause" class="w-4 h-4 fill-current"></i>';
            } else {
                audioElement.pause();
                playPauseBtn.innerHTML = '<i data-lucide="play" class="w-4 h-4 fill-current"></i>';
            }
            lucide.createIcons();
        });

        audioElement.addEventListener('timeupdate', () => {
            const percent = (audioElement.currentTime / audioElement.duration) * 100;
            audioProgress.style.width = `${percent}%`;
        });

        audioElement.addEventListener('ended', () => {
            playPauseBtn.innerHTML = '<i data-lucide="play" class="w-4 h-4 fill-current"></i>';
            audioProgress.style.width = '0%';
            lucide.createIcons();
        });
    }

    if (deleteAudioBtn) {
        deleteAudioBtn.addEventListener('click', async () => {
            if (confirm('Remove audio?')) {
                audioElement.pause();
                audioElement.src = '';
                audioPreview.classList.add('hidden');
                state.voiceMessageUrl = null;

                // Update backend to remove voice
                if (state.invitationId || window.currentInvitationId) {
                    await saveVoiceToInvitation(state.invitationId || window.currentInvitationId, null);
                }
            }
        });
    }

});

// Music Modal Functions (Global scope for onclick handlers)
function openMusicModal() {
    const modal = document.getElementById('musicModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');

        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

function closeMusicModal() {
    const modal = document.getElementById('musicModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

async function generateVideoWithMusic(musicChoice) {
    closeMusicModal();

    const generateVideoBtn = document.getElementById('generateVideoBtn');
    const originalHTML = generateVideoBtn.innerHTML;
    generateVideoBtn.innerHTML = '<div class="spinner"></div> Generating Video (30-60s)...';
    generateVideoBtn.disabled = true;

    try {
        // Get invitation_id from multiple possible sources
        const resultSection = document.getElementById('resultSection');
        const invitation_id = window.currentInvitationId ||
            resultSection?.dataset?.invitationId ||
            document.querySelector('[data-invitation-id]')?.dataset.invitationId;

        console.log('🎬 Starting video generation...');
        console.log('Invitation ID:', invitation_id);
        console.log('Music choice:', musicChoice);

        if (!invitation_id) {
            throw new Error('No invitation found. Please generate an invitation first.');
        }

        console.log('Sending request to /api/generate-video...');

        const response = await fetch('/api/generate-video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                invitation_id: invitation_id,
                music: musicChoice,
                duration: 12 // 12 seconds (10-15s range)
            })
        });

        console.log('Response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error:', errorText);
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        console.log('Response data:', result);

        if (!result.success) {
            throw new Error(result.error || 'Failed to generate video');
        }

        console.log('✅ Video generated successfully!');
        console.log('Video URL:', result.video_url);

        // Show download button
        const downloadVideoBtn = document.getElementById('downloadVideoBtn');
        if (downloadVideoBtn) {
            downloadVideoBtn.href = result.video_url;
            downloadVideoBtn.classList.remove('hidden');
            console.log('Download button shown');
        }

        alert('🎉 Video generated successfully! Click the "Download Video" button to save it.');

    } catch (error) {
        console.error('❌ Video generation error:', error);
        console.error('Error details:', error.message);
        alert(`Error generating video:\n${error.message}\n\nCheck browser console (F12) for details.`);
    } finally {
        generateVideoBtn.innerHTML = originalHTML;
        generateVideoBtn.disabled = false;

        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
}

// Close modal on outside click
document.getElementById('musicModal')?.addEventListener('click', function (e) {
    if (e.target === this) {
        closeMusicModal();
    }
});

// Initialize Lucide icons
if (typeof lucide !== 'undefined') {
    lucide.createIcons();
}

// --- TEXT EDITING FUNCTIONS (GLOBAL) ---

// State for edit mode
let isEditMode = false;

// Toggle Edit Mode
window.toggleEditMode = function () {
    console.log('toggleEditMode called');
    const styleControls = document.getElementById('styleControls');
    const editBtn = document.getElementById('editTextBtn');
    const cardTitle = document.getElementById('cardTitle');
    const cardBody = document.getElementById('cardBody');

    if (!cardTitle || !cardBody) {
        console.error('Text elements not found for editing');
        return;
    }

    isEditMode = !isEditMode;
    console.log('Edit mode:', isEditMode);

    if (isEditMode) {
        // Enter Edit Mode
        cardTitle.contentEditable = true;
        cardBody.contentEditable = true;

        // Make all editable text elements focusable
        cardTitle.focus();

        // Show style controls
        if (styleControls) {
            styleControls.classList.remove('hidden');
            styleControls.classList.add('flex');
        }

        // Update button appearance
        if (editBtn) {
            editBtn.innerHTML = '<i data-lucide="check" class="w-4 h-4"></i> Done';
            editBtn.classList.remove('bg-black/50', 'hover:bg-black/70');
            editBtn.classList.add('bg-green-500/70', 'hover:bg-green-600');
        }

        // Add editing visual feedback
        cardTitle.classList.add('ring-2', 'ring-purple-500/50', 'bg-black/20');
        cardBody.classList.add('ring-2', 'ring-purple-500/50', 'bg-black/20');

    } else {
        // Exit Edit Mode
        cardTitle.contentEditable = false;
        cardBody.contentEditable = false;

        // Hide style controls
        if (styleControls) {
            styleControls.classList.add('hidden');
            styleControls.classList.remove('flex');
        }

        // Update button appearance
        if (editBtn) {
            editBtn.innerHTML = '<i data-lucide="edit-3" class="w-4 h-4"></i> Edit Text';
            editBtn.classList.add('bg-black/50', 'hover:bg-black/70');
            editBtn.classList.remove('bg-green-500/70', 'hover:bg-green-600');
        }

        // Remove editing visual feedback
        cardTitle.classList.remove('ring-2', 'ring-purple-500/50', 'bg-black/20');
        cardBody.classList.remove('ring-2', 'ring-purple-500/50', 'bg-black/20');
    }

    // Reinitialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
};

// Change Font Style
window.changeFont = function (fontClass) {
    const cardTitle = document.getElementById('cardTitle');
    const cardBody = document.getElementById('cardBody');
    if (!cardTitle || !cardBody) return;

    const fontClasses = ['font-sans', 'font-serif', 'font-mono', 'font-display'];

    // Remove existing font classes
    fontClasses.forEach(fc => {
        cardTitle.classList.remove(fc);
        cardBody.classList.remove(fc);
    });

    // Add new font class
    cardTitle.classList.add(fontClass);
    cardBody.classList.add(fontClass);

    console.log('Font changed to:', fontClass);
};

// Change Text Color (using hex values for direct styling)
window.changeColor = function (hexColor) {
    const cardTitle = document.getElementById('cardTitle');
    const cardBody = document.getElementById('cardBody');

    if (cardTitle) cardTitle.style.color = hexColor;
    if (cardBody) cardBody.style.color = hexColor;

    // Also update event details text
    const dateText = document.getElementById('dateText');
    const timeText = document.getElementById('timeText');
    const venueText = document.getElementById('venueText');
    const familyNameText = document.getElementById('familyNameText');

    if (dateText) dateText.style.color = hexColor;
    if (timeText) timeText.style.color = hexColor;
    if (venueText) venueText.style.color = hexColor;
    if (familyNameText) familyNameText.style.color = hexColor;

    console.log('Color changed to:', hexColor);
};

// Change Font Size (percentage-based scaling)
window.changeFontSize = function (percentage) {
    const cardTitle = document.getElementById('cardTitle');
    if (!cardTitle) return;

    const scale = percentage / 100;

    // Update the display value
    const fontSizeValue = document.getElementById('fontSizeValue');
    if (fontSizeValue) {
        fontSizeValue.textContent = percentage;
    }

    // Apply transform scale to title (keeps it responsive)
    cardTitle.style.transform = `scale(${scale})`;
    cardTitle.style.transformOrigin = 'center';

    console.log('Font size changed to:', percentage + '%');
};

// Toggle Text Shadow
window.toggleTextShadow = function (enabled) {
    const cardTitle = document.getElementById('cardTitle');
    const cardBody = document.getElementById('cardBody');

    const shadowStyle = enabled ? '0 4px 20px rgba(0,0,0,0.8), 0 2px 10px rgba(0,0,0,0.6)' : 'none';

    if (cardTitle) cardTitle.style.textShadow = shadowStyle;
    if (cardBody) cardBody.style.textShadow = shadowStyle;

    // Update other text elements
    const dateText = document.getElementById('dateText');
    const timeText = document.getElementById('timeText');
    const venueText = document.getElementById('venueText');
    const familyNameText = document.getElementById('familyNameText');

    if (dateText) dateText.style.textShadow = shadowStyle;
    if (timeText) timeText.style.textShadow = shadowStyle;
    if (venueText) venueText.style.textShadow = shadowStyle;
    if (familyNameText) familyNameText.style.textShadow = shadowStyle;

    console.log('Text shadow:', enabled ? 'enabled' : 'disabled');
};

// Preview Audio Function (Direct Streaming)
window.previewAudio = function (musicKey, btn) {
    event.stopPropagation(); // Prevent card selection

    const audioPlayer = document.getElementById('musicPreviewPlayer');
    // Map keys to direct streaming URLs (using SoundHelix or similar stable test files)
    const musicMap = {
        'happy_birthday': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-1.mp3',
        'wedding_bells': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-2.mp3',
        'party_time': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-3.mp3',
        'celebration': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-4.mp3',
        'elegant_classic': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-5.mp3',
        'upbeat_pop': 'https://www.soundhelix.com/media/mp3/SoundHelix-Song-6.mp3'
    };

    if (!musicMap[musicKey]) {
        console.warn("No music URL for:", musicKey);
        return;
    }

    const currentSrc = audioPlayer.src;
    const newSrc = musicMap[musicKey];

    // Reset all other buttons to Play icon
    const allPreviewBtns = document.querySelectorAll('button[onclick^="playMusicPreview"]');
    allPreviewBtns.forEach(b => {
        if (b !== btn) {
            b.innerHTML = '<i data-lucide="play" class="w-4 h-4 fill-current"></i>';
        }
    });

    if (currentSrc === newSrc && !audioPlayer.paused) {
        // Pause current
        audioPlayer.pause();
        btn.innerHTML = '<i data-lucide="play" class="w-4 h-4 fill-current"></i>';
    } else {
        // Play new
        audioPlayer.src = newSrc;
        const playPromise = audioPlayer.play();
        
        if (playPromise !== undefined) {
            btn.innerHTML = '<div class="spinner border-2 border-current border-r-transparent w-4 h-4 rounded-full animate-spin"></div>';
            
            playPromise.then(_ => {
                // Automatic playback started!
                btn.innerHTML = '<i data-lucide="pause" class="w-4 h-4 fill-current"></i>';
                if (typeof lucide !== 'undefined') lucide.createIcons();
            })
            .catch(error => {
                console.error("Audio play error:", error);
                btn.innerHTML = '<i data-lucide="alert-circle" class="w-4 h-4 text-red-500"></i>';
                if (typeof lucide !== 'undefined') lucide.createIcons();
            });
        }
    }
    
    if (typeof lucide !== 'undefined') lucide.createIcons();
};

