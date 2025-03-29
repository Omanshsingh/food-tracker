// static/js/watertracker.js
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const addGlassBtn = document.getElementById('add-glass');
    const removeGlassBtn = document.getElementById('remove-glass');
    const glassCount = document.getElementById('glass-count');
    const progressBar = document.querySelector('.progress-bar');
    const quickAddBtns = document.querySelectorAll('.quick-add');
    const customAddBtn = document.getElementById('add-custom');
    const customAmountInput = document.getElementById('custom-amount');
    const waterLog = document.getElementById('water-log');

    // Update display function
    function updateDisplay(data) {
        glassCount.textContent = data.glasses;
        progressBar.style.width = `${data.progress}%`;
        progressBar.setAttribute('aria-valuenow', data.progress);
        progressBar.innerHTML = `<span class="fw-bold">${data.glasses}/{{ water_goal.daily_goal }} glasses</span>`;
    }

    // Handle water actions
    function handleWaterAction(action, amount = null) {
        const formData = new FormData();
        formData.append('action', action);
        if (amount) formData.append('amount', amount);

        fetch("{% url 'log_water' %}", {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
            },
            body: formData
        })
        .then(response => response.json())
        .then(updateDisplay);
    }

    // Event listeners
    addGlassBtn.addEventListener('click', () => handleWaterAction('add'));
    removeGlassBtn.addEventListener('click', () => handleWaterAction('remove'));
    
    quickAddBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            handleWaterAction('add', this.dataset.amount);
        });
    });
    
    customAddBtn.addEventListener('click', function() {
        const amount = parseInt(customAmountInput.value);
        if (!isNaN(amount)) {
            handleWaterAction('add', amount);
            customAmountInput.value = '';
        }
    });

    // Initialize log display
    function updateLogDisplay() {
        fetch("{% url 'get_water_log' %}")
            .then(response => response.json())
            .then(data => {
                waterLog.innerHTML = data.log.map(entry => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between">
                            <span>${entry.amount}ml</span>
                            <small class="text-muted">${new Date(entry.timestamp).toLocaleTimeString()}</small>
                        </div>
                    </div>
                `).join('');
            });
    }

    // Initial load
    updateLogDisplay();
});