// Wait for DOM and all resources to load
document.addEventListener("DOMContentLoaded", function() {
    // Get chart data from DOM
    const getChartData = () => {
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
    };

    // Calculate water intake totals and progress
    const calculateWaterData = () => {
        const currentGlasses = document.getElementById('currentGlasses');
        const dailyGoal = document.getElementById('dailyGoal');
        
        if (!currentGlasses || !dailyGoal) return null;
        
        const waterIntake = parseInt(currentGlasses.textContent) || 0;
        const waterGoal = parseInt(dailyGoal.textContent) || 8;
        const progress = Math.min(Math.round((waterIntake / waterGoal) * 100), 100);
        
        return {
            glasses: waterIntake,
            goal: waterGoal,
            progress: progress,
            remaining: Math.max(0, waterGoal - waterIntake)
        };
    };
  
    // Initialize water chart
    const initWaterChart = () => {
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
    };
  
    // Update UI elements with water data
    const updateWaterUI = (waterData) => {
        if (!waterData) return;
        
        const { glasses, goal, progress, remaining } = waterData;
        
        // Update progress bar
        const progressBar = document.getElementById('waterProgressBar');
        if (progressBar) {
            progressBar.style.width = progress + '%';
            progressBar.setAttribute('aria-valuenow', glasses);
            progressBar.textContent = `${glasses}/${goal} glasses`;
            
            // Update progress bar color based on percentage
            progressBar.className = 'progress-bar progress-bar-striped ' + 
                (progress >= 100 ? 'bg-success' :
                 progress >= 75 ? 'bg-info' :
                 progress > 0 ? 'bg-warning' : 'bg-danger');
        }
        
        // Update glass counter
        const currentGlasses = document.getElementById('currentGlasses');
        if (currentGlasses) {
            currentGlasses.textContent = glasses;
        }
        
        // Update status text
        const statusElement = document.getElementById('waterStatus');
        if (statusElement) {
            if (glasses === 0) {
                statusElement.textContent = "Not started";
                statusElement.className = "text-danger mb-2";
            } else if (glasses < goal * 0.5) {
                statusElement.textContent = "Low hydration";
                statusElement.className = "text-warning mb-2";
            } else if (glasses < goal) {
                statusElement.textContent = "Good progress";
                statusElement.className = "text-info mb-2";
            } else if (glasses === goal) {
                statusElement.textContent = "Goal achieved!";
                statusElement.className = "text-success mb-2";
            } else {
                statusElement.textContent = "Overachiever!";
                statusElement.className = "text-primary mb-2";
            }
        }
        
        // Update remaining text
        const remainingElement = document.getElementById('remainingText');
        if (remainingElement) {
            remainingElement.textContent = glasses < goal 
                ? `${remaining} more glasses to reach your goal!` 
                : "You've met your daily goal!";
        }
    };
  
    // Handle water logging via AJAX
    const handleWaterLog = async (action) => {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            if (!csrfToken) throw new Error('CSRF token missing');
            
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
            updateWaterUI({
                glasses: data.glasses,
                goal: data.goal || parseInt(document.getElementById('dailyGoal').textContent),
                progress: data.progress,
                remaining: (data.goal || parseInt(document.getElementById('dailyGoal').textContent)) - data.glasses
            });
            
            // Visual feedback
            const btn = document.getElementById(action === 'add' ? 'addWater' : 'removeWater');
            btn.classList.add('btn-pulse');
            setTimeout(() => btn.classList.remove('btn-pulse'), 300);
            
        } catch (error) {
            console.error('Error logging water:', error);
            // Visual error feedback
            const counter = document.getElementById('currentGlasses');
            if (counter) {
                counter.classList.add('text-danger', 'shake');
                setTimeout(() => {
                    counter.classList.remove('text-danger', 'shake');
                }, 1000);
            }
        }
    };
  
    // Initialize everything
    const init = () => {
        const waterData = calculateWaterData();
        updateWaterUI(waterData);
        initWaterChart();
        
        // Event listeners for buttons
        const addBtn = document.getElementById('addWater');
        const removeBtn = document.getElementById('removeWater');
        
        if (addBtn) addBtn.addEventListener('click', () => handleWaterLog('add'));
        if (removeBtn) removeBtn.addEventListener('click', () => handleWaterLog('remove'));
    };
    
    init();
});

// Add some basic animations
document.head.insertAdjacentHTML('beforeend', `
    <style>
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
    </style>
`);