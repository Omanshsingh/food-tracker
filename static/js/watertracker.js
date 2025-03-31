document.addEventListener("DOMContentLoaded", function() {
    // =============================================
    // 1. INITIALIZATION
    // =============================================
    
    // Get DOM elements
    const currentGlassesEl = document.getElementById('currentGlasses');
    const dailyGoalEl = document.getElementById('dailyGoal');
    const progressBarEl = document.getElementById('waterProgressBar');
    const statusEl = document.getElementById('waterStatus');
    const remainingEl = document.getElementById('remainingText');
    const addBtn = document.getElementById('addWater');
    const removeBtn = document.getElementById('removeWater');
    const settingsForm = document.getElementById('water-settings-form');
    const reminderCheckbox = document.getElementById('reminder-enabled');
    const reminderInterval = document.getElementById('reminder-interval');

    // =============================================
    // 2. CHART FUNCTIONS
    // =============================================

    function initWaterChart() {
        const chartEl = document.getElementById('weeklyWaterChart');
        if (!chartEl || typeof Chart === 'undefined') return;

        const chartData = getChartData();
        if (!chartData) return;

        Chart.defaults.font.family = 'Poppins, sans-serif';
        Chart.defaults.color = '#858796';

        new Chart(chartEl.getContext('2d'), {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'Glasses Consumed',
                        data: chartData.intake,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Daily Goal',
                        data: Array(chartData.labels.length).fill(chartData.goal),
                        type: 'line',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 2,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + context.raw + ' glasses';
                            }
                        }
                    }
                }
            }
        });
    }

    function getChartData() {
        const dataEl = document.getElementById('chartData');
        if (!dataEl) return null;
        
        try {
            return {
                labels: dataEl.dataset.labels.split(','),
                intake: dataEl.dataset.intake.split(',').map(Number),
                goal: parseInt(dataEl.dataset.goal) || 8
            };
        } catch (error) {
            console.error('Error parsing chart data:', error);
            return null;
        }
    }

    // =============================================
    // 3. WATER LOGGING FUNCTIONS
    // =============================================

    async function logWater(action) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await fetch("{% url 'log_water' %}", {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `action=${action}`
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            updateWaterUI(data.glasses);
            
            // Visual feedback
            const btn = action === 'add' ? addBtn : removeBtn;
            btn.classList.add('btn-pulse');
            setTimeout(() => btn.classList.remove('btn-pulse'), 300);
            
        } catch (error) {
            console.error('Error logging water:', error);
            showAlert('Error updating water intake', 'danger');
        }
    }

    // =============================================
    // 4. SETTINGS FORM HANDLING
    // =============================================

    function setupSettingsForm() {
        if (!settingsForm) return;

        // Enable/disable reminder interval based on checkbox
        if (reminderCheckbox && reminderInterval) {
            reminderInterval.disabled = !reminderCheckbox.checked;
            reminderCheckbox.addEventListener('change', function() {
                reminderInterval.disabled = !this.checked;
            });
        }

        settingsForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitBtn = this.querySelector('button[type="submit"]');
            
            try {
                // Disable button during submission
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
                }

                const formData = new FormData(this);
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': '{{ csrf_token }}'
                    }
                });

                if (response.redirected) {
                    window.location.href = response.url;  // Full page reload to ensure updates
                } else {
                    const data = await response.json();
                    if (data && data.status === 'error') {
                        throw new Error(data.message);
                    }
                    updateReminderDisplay();
                    showAlert('Settings saved successfully!', 'success');
                }
            } catch (error) {
                console.error('Error saving settings:', error);
                showAlert('Error saving settings: ' + error.message, 'danger');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Save Changes';
                }
            }
        });
    }

    function updateReminderDisplay() {
        const reminderStatusEl = document.getElementById('reminderStatus');
        if (!reminderStatusEl) return;

        if (reminderCheckbox && reminderInterval) {
            const isEnabled = reminderCheckbox.checked;
            const interval = reminderInterval.value;
            
            reminderStatusEl.textContent = isEnabled 
                ? `Enabled (${interval} min intervals)` 
                : 'Disabled';
            reminderStatusEl.className = isEnabled ? 'text-success' : 'text-secondary';
        }
    }

    // =============================================
    // 5. UI UPDATE FUNCTIONS
    // =============================================

    function updateWaterUI(glasses = null) {
        // Get current values
        const currentGlasses = glasses !== null ? glasses : parseInt(currentGlassesEl?.textContent) || 0;
        const goal = parseInt(dailyGoalEl?.textContent) || 8;
        const progress = Math.min(Math.round((currentGlasses / goal) * 100), 100);
        const remaining = Math.max(0, goal - currentGlasses);

        // Update progress bar
        if (progressBarEl) {
            progressBarEl.style.width = progress + '%';
            progressBarEl.setAttribute('aria-valuenow', currentGlasses);
            progressBarEl.textContent = `${currentGlasses}/${goal} glasses`;
            
            // Update progress bar color
            progressBarEl.className = 'progress-bar progress-bar-striped ' + 
                (progress >= 100 ? 'bg-success' :
                 progress >= 75 ? 'bg-info' :
                 progress > 0 ? 'bg-warning' : 'bg-danger');
        }

        // Update status text
        if (statusEl) {
            if (currentGlasses === 0) {
                statusEl.textContent = "Not started";
                statusEl.className = "text-danger mb-2";
            } else if (currentGlasses < goal * 0.5) {
                statusEl.textContent = "Low hydration";
                statusEl.className = "text-warning mb-2";
            } else if (currentGlasses < goal) {
                statusEl.textContent = "Good progress";
                statusEl.className = "text-info mb-2";
            } else if (currentGlasses === goal) {
                statusEl.textContent = "Goal achieved!";
                statusEl.className = "text-success mb-2";
            } else {
                statusEl.textContent = "Overachiever!";
                statusEl.className = "text-primary mb-2";
            }
        }

        // Update remaining text
        if (remainingEl) {
            remainingEl.textContent = currentGlasses < goal 
                ? `${remaining} more glasses to reach your goal!` 
                : "You've met your daily goal!";
        }
    }

    // =============================================
    // 6. HELPER FUNCTIONS
    // =============================================

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-3`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container-fluid') || document.body;
        container.prepend(alertDiv);
        
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 5000);
    }

    function setupWaterLogButtons() {
        if (addBtn) addBtn.addEventListener('click', () => logWater('add'));
        if (removeBtn) removeBtn.addEventListener('click', () => logWater('remove'));
    }

    function addWaterTrackerStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .btn-pulse {
                animation: pulse 0.3s ease;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            .shake {
                animation: shake 0.5s ease;
            }
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                20%, 60% { transform: translateX(-5px); }
                40%, 80% { transform: translateX(5px); }
            }
        `;
        document.head.appendChild(style);
    }

    // =============================================
    // 7. INITIAL SETUP
    // =============================================
    
    initWaterChart();
    updateWaterUI();
    updateReminderDisplay();
    setupWaterLogButtons();
    setupSettingsForm();
});
