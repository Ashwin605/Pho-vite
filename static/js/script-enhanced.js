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
        selectedMusic: null
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
                <div class="glass-card rounded-xl p-6 md:p-8 border-2 border-white/20 hover:border-purple-400/50 transition-all duration-300 h-32 md:h-40 flex flex-col justify-center items-center touch-manipulation cursor-pointer">
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
        switch(eventType) {
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
        
        switch(state.eventType) {
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

            // Step 1: Refine Prompt with Enhanced Details (Gemini)
            updateProgressStep(1, 'active');
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
            updateProgressStep(1, 'completed');
            
            // Small delay for visual feedback
            await new Promise(resolve => setTimeout(resolve, 500));

            // Step 2: Generate Image & Process Photos
            updateProgressStep(2, 'active');
            const imageResponse = await fetch('/api/generate-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_prompt: state.generatedData.image_prompt,
                    user_photo_url: state.userPhotoUrl,
                    title: state.generatedData.card_title,
                    body: state.generatedData.card_body,
                    eventType: state.eventType,
                    vibe: state.vibe,
                    familyName: state.familyName,
                    celebrantName: state.celebrantName,
                    eventDate: state.eventDate,
                    eventTime: state.eventTime,
                    eventVenue: state.eventVenue,
                    eventMessage: state.eventMessage,
                    location_name: state.eventVenue,
                    ...eventSpecificData  // Spread event-specific data
                })
            });

            const imageResult = await imageResponse.json();
            if (!imageResult.success) throw new Error(imageResult.error);

            updateProgressStep(2, 'completed');
            await new Promise(resolve => setTimeout(resolve, 500));

            // Step 3: Compositing
            updateProgressStep(3, 'active');
            await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate compositing time
            updateProgressStep(3, 'completed');
            await new Promise(resolve => setTimeout(resolve, 500));

            // Step 4: Finalizing
            updateProgressStep(4, 'active');
            
            // Store invitation data FIRST (before displaying)
            if (imageResult.invitation_id) {
                state.invitation_id = imageResult.invitation_id;
                state.share_link = imageResult.share_link;
                console.log('Invitation created with ID:', state.invitation_id);
            }

            await new Promise(resolve => setTimeout(resolve, 800));
            updateProgressStep(4, 'completed');

            // Hide progress and display results
            await new Promise(resolve => setTimeout(resolve, 500));
            hideProgressIndicator();
            
            // Display results and auto-scroll to preview
            displayResults(imageResult.image_url);
            
            // Auto-scroll to result section
            setTimeout(() => {
                resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 300);

        } catch (error) {
            console.error('Generation error:', error);
            hideProgressIndicator();
            alert(`Error: ${error.message}`);
        } finally {
            setButtonLoading(generateBtn, false);
        }
    });

    function displayResults(imageUrl) {
        // Show result section
        resultSection.classList.remove('hidden');
        inputForm.scrollIntoView({ behavior: 'smooth' });

        // Set background image
        generatedImage.src = imageUrl;
        generatedImage.style.display = 'block';
        skeletonLoader.style.display = 'none';

        // Display text elements (Photos are already in the composited background image)
        const familyNameText = document.getElementById('familyNameText');
        if (familyNameText) {
            familyNameText.textContent = state.familyName;
        }

        // Display celebrant name
        if (cardTitle) {
            cardTitle.textContent = state.celebrantName;
        }

        // Display event details
        const dateText = document.getElementById('dateText');
        const timeText = document.getElementById('timeText');
        const venueText = document.getElementById('venueText');

        if (dateText) dateText.textContent = state.eventDate;
        if (timeText) timeText.textContent = state.eventTime;
        if (venueText) venueText.textContent = state.eventVenue;

        // Display message
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

        // Store invitation_id globally for video generation
        if (state.invitation_id) {
            window.currentInvitationId = state.invitation_id;
            // Also store in a data attribute on the result section
            resultSection.dataset.invitationId = state.invitation_id;
            console.log('Invitation ID stored:', state.invitation_id);
        }

        // Reinitialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }

        // Scroll to results
        setTimeout(() => {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 500);
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
document.getElementById('musicModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        closeMusicModal();
    }
});

// Initialize Lucide icons
if (typeof lucide !== 'undefined') {
    lucide.createIcons();
}

