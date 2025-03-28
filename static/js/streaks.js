document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab functionality with proper event delegation
    const streakTabs = document.getElementById('streakTabs');
    if (streakTabs) {
        streakTabs.addEventListener('click', function(event) {
            if (event.target.tagName === 'BUTTON' || event.target.closest('button')) {
                const tabButton = event.target.tagName === 'BUTTON' ? event.target : event.target.closest('button');
                const tabId = tabButton.getAttribute('data-bs-target');
                const tabPane = document.querySelector(tabId);
                
                // Ensure the tab content is visible
                if (tabPane) {
                    document.querySelectorAll('.tab-pane').forEach(pane => {
                        pane.classList.remove('show', 'active');
                    });
                    tabPane.classList.add('show', 'active');
                    
                    // Update active tab button
                    document.querySelectorAll('.nav-link').forEach(link => {
                        link.classList.remove('active');
                    });
                    tabButton.classList.add('active');
                }
            }
        });
    }

    // Get streak data and initialize animations
    const initializeStreak = () => {
        const flame = document.querySelector('.streak-flame');
        if (!flame) return;

        const currentStreak = parseInt(document.querySelector('.streak-count')?.textContent || '0');
        
        if (currentStreak > 0) {
            flame.classList.add('animate__animated', 'animate__pulse');
            
            // Special celebration for milestones
            if (currentStreak % 5 === 0) {
                flame.classList.add('text-warning');
                triggerConfetti();
            }
        }
    };

    // Confetti animation with better cleanup
    const triggerConfetti = () => {
        setTimeout(() => {
            const confettiSettings = {
                target: 'confetti',
                max: 80,
                size: 1.5,
                animate: true,
                props: ['circle', 'square', 'triangle', 'line'],
                colors: [
                    [67, 97, 238],  // Primary color
                    [76, 201, 240], // Accent color
                    [255, 87, 34],  // Flame color
                    [255, 215, 0]   // Gold
                ]
            };
            
            try {
                const confetti = new ConfettiGenerator(confettiSettings);
                const confettiCanvas = document.getElementById('confetti');
                
                if (confettiCanvas) {
                    confetti.render();
                    confettiCanvas.style.display = 'block';
                    
                    setTimeout(() => {
                        confetti.clear();
                        confettiCanvas.style.display = 'none';
                    }, 3000);
                }
            } catch (e) {
                console.error('Confetti error:', e);
            }
        }, 500);
    };

    // Initialize everything
    initializeStreak();

    // Add click handlers for any interactive elements
    document.querySelectorAll('.streak-container, .streak-flame').forEach(element => {
        element.style.cursor = 'pointer';
        element.addEventListener('click', function() {
            // Add any specific click behavior here
            console.log('Streak element clicked');
        });
    });
});