// ======================
// FOOD LOGGING FUNCTIONS
// ======================

// Initialize storage on page load
document.addEventListener('DOMContentLoaded', function() {
    if (!localStorage.getItem('foodItems')) {
      localStorage.setItem('foodItems', JSON.stringify([]));
    }
    displayFoodItems();
    updateStreak();
  });
  
  // Add food to log
  function addFoodToLog(foodItem) {
    const foodItems = JSON.parse(localStorage.getItem('foodItems')) || [];
    foodItems.push({
      ...foodItem,
      timestamp: new Date().toISOString() // Critical for streaks
    });
    localStorage.setItem('foodItems', JSON.stringify(foodItems));
    displayFoodItems();
    updateStreak();
  }
  
  // Display all food items
  function displayFoodItems() {
    const foodItems = JSON.parse(localStorage.getItem('foodItems')) || [];
    const foodLog = document.getElementById('food-log');
    
    foodLog.innerHTML = foodItems.map(item => `
      <div class="food-item">
        <span>${item.name}</span>
        <span>${item.calories} cal</span>
        <button onclick="removeFood('${item.timestamp}')">×</button>
      </div>
    `).join('');
  }
  
  // Remove food item
  function removeFood(timestamp) {
    let foodItems = JSON.parse(localStorage.getItem('foodItems')) || [];
    foodItems = foodItems.filter(item => item.timestamp !== timestamp);
    localStorage.setItem('foodItems', JSON.stringify(foodItems));
    displayFoodItems();
    updateStreak();
  }
  
  // ==================
  // HELPER FUNCTIONS
  // ==================
  
  function getTotalCalories() {
    const foodItems = JSON.parse(localStorage.getItem('foodItems')) || [];
    return foodItems.reduce((total, item) => total + Number(item.calories), 0);
  }
  /* ===== DROPDOWN OVERLAP FIX ===== */
.nav-item.dropdown .dropdown-menu {
  z-index: 1050 !important; /* Ensures dropdown stays on top */
  overflow: hidden;
}

.nav-item.dropdown .dropdown-item {
  white-space: nowrap;
  display: flex !important;
  justify-content: space-between;
  align-items: center;
  min-width: 220px;
}

.nav-item.dropdown .badge {
  flex-shrink: 0;
  margin-left: 12px;
}