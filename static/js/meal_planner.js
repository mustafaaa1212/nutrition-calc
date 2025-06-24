// Meal Planner JavaScript functionality

class MealPlanner {
    constructor() {
        this.selectedIngredients = [];
        this.nutritionChart = null;
        this.initializeEventListeners();
        this.loadIngredients();
    }

    initializeEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('ingredientSearch');
        const categoryFilter = document.getElementById('categoryFilter');
        
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => {
                this.searchIngredients();
            }, 300));
        }
        
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => {
                this.searchIngredients();
            });
        }

        // Calculate button
        const calculateBtn = document.getElementById('calculateBtn');
        if (calculateBtn) {
            calculateBtn.addEventListener('click', () => {
                this.calculateNutrition();
            });
        }

        // Add ingredient buttons (delegated event handling)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-ingredient') || 
                e.target.closest('.add-ingredient')) {
                const button = e.target.closest('.add-ingredient') || e.target;
                const ingredientItem = button.closest('.ingredient-item');
                if (ingredientItem) {
                    this.addIngredient(ingredientItem);
                }
            }
        });

        // Remove ingredient functionality
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-ingredient') || 
                e.target.closest('.remove-ingredient')) {
                const button = e.target.closest('.remove-ingredient') || e.target;
                const ingredientId = button.dataset.id;
                if (ingredientId) {
                    this.removeIngredient(parseInt(ingredientId));
                }
            }
        });

        // Quantity change functionality
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                const ingredientId = parseInt(e.target.dataset.id);
                const quantity = parseFloat(e.target.value) || 0;
                this.updateIngredientQuantity(ingredientId, quantity);
            }
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    async loadIngredients() {
        try {
            const response = await fetch('/search-ingredients');
            if (response.ok) {
                const ingredients = await response.json();
                this.displayIngredients(ingredients);
            }
        } catch (error) {
            console.error('Error loading ingredients:', error);
            this.showError('Error loading ingredients');
        }
    }

    async searchIngredients() {
        const query = document.getElementById('ingredientSearch')?.value || '';
        const category = document.getElementById('categoryFilter')?.value || '';
        
        const params = new URLSearchParams();
        if (query) params.append('q', query);
        if (category) params.append('category', category);

        try {
            const response = await fetch(`/search-ingredients?${params}`);
            if (response.ok) {
                const ingredients = await response.json();
                this.displayIngredients(ingredients);
            }
        } catch (error) {
            console.error('Error searching ingredients:', error);
            this.showError('Error searching ingredients');
        }
    }

    displayIngredients(ingredients) {
        const container = document.getElementById('ingredientResults');
        if (!container) return;

        if (ingredients.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <i class="fas fa-search fa-2x mb-2"></i>
                    <p>No ingredients found. Try a different search term.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = ingredients.map(ingredient => {
            // Check if ingredient is already selected
            const isSelected = this.selectedIngredients.find(ing => ing.id === ingredient.id);
            const buttonClass = isSelected ? 'btn-secondary disabled' : 'btn-outline-primary';
            const buttonText = isSelected ? 'Added' : 'Add';
            const buttonIcon = isSelected ? 'fa-check' : 'fa-plus';
            
            return `
                <div class="ingredient-item border rounded p-2 mb-2" data-id="${ingredient.id}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${ingredient.name}</strong>
                            <small class="text-muted d-block">${ingredient.category || 'Unknown'}</small>
                            <small class="text-info">${ingredient.calories} cal/100g</small>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <input type="number" class="form-control form-control-sm portion-input" 
                                   placeholder="grams" min="1" max="5000" step="1" style="width: 80px;"
                                   ${isSelected ? 'disabled' : ''}>
                            <button class="btn btn-sm ${buttonClass} add-ingredient" ${isSelected ? 'disabled' : ''}>
                                <i class="fas ${buttonIcon}"></i> ${buttonText}
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Add event listeners for quantity changes
        container.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', (e) => {
                const ingredientId = parseInt(e.target.dataset.id);
                const newQuantity = parseFloat(e.target.value) || 100;
                if (newQuantity > 0 && newQuantity <= 5000) {
                    this.updateIngredientQuantity(ingredientId, newQuantity);
                } else {
                    this.showWarning('Please enter a valid portion size (1-5000 grams).');
                    const ingredient = this.selectedIngredients.find(ing => ing.id === ingredientId);
                    if (ingredient) {
                        e.target.value = ingredient.quantity;
                    }
                }
            });
        });
        
        // Add event listeners for removal
        container.querySelectorAll('.remove-ingredient').forEach(button => {
            button.addEventListener('click', (e) => {
                const ingredientId = parseInt(e.target.dataset.id);
                this.removeIngredient(ingredientId);
            });
        });
    }

    addIngredient(ingredientItem) {
        const id = parseInt(ingredientItem.dataset.id);
        const name = ingredientItem.querySelector('strong').textContent;
        const category = ingredientItem.querySelector('.text-muted').textContent;
        const calories = ingredientItem.querySelector('.text-info').textContent;

        // Check if already added
        if (this.selectedIngredients.find(ing => ing.id === id)) {
            this.showWarning(`${name} is already in your meal plan`);
            return;
        }

        // Get portion size from input field if available
        const portionInput = ingredientItem.querySelector('.portion-input');
        const quantity = portionInput ? (parseFloat(portionInput.value) || 100) : 100;
        
        // Validate portion size
        if (quantity <= 0 || quantity > 5000) {
            this.showWarning('Please enter a valid portion size (1-5000 grams).');
            return;
        }

        // Add to selected ingredients
        const ingredient = {
            id: id,
            name: name,
            category: category,
            calories: calories,
            quantity: quantity
        };

        this.selectedIngredients.push(ingredient);
        
        // Clear the portion input if it exists
        if (portionInput) {
            portionInput.value = '';
        }
        
        this.updateSelectedIngredientsDisplay();
        this.updateSaveMealForm();
        
        // Refresh the ingredient list to update button states
        this.searchIngredients();
        
        this.showSuccess(`${name} (${quantity}g) added to meal plan`);
    }

    removeIngredient(ingredientId) {
        const removedIngredient = this.selectedIngredients.find(ing => ing.id === ingredientId);
        this.selectedIngredients = this.selectedIngredients.filter(ing => ing.id !== ingredientId);
        this.updateSelectedIngredientsDisplay();
        this.updateSaveMealForm();
        
        // Refresh the ingredient list to show the add button again
        this.searchIngredients();
        
        // Hide nutrition results if no ingredients
        if (this.selectedIngredients.length === 0) {
            document.getElementById('nutritionResults').style.display = 'none';
        }
        
        if (removedIngredient) {
            this.showSuccess(`${removedIngredient.name} removed from meal plan`);
        }
    }

    updateIngredientQuantity(ingredientId, quantity) {
        const ingredient = this.selectedIngredients.find(ing => ing.id === ingredientId);
        if (ingredient) {
            ingredient.quantity = Math.max(1, quantity);
            this.updateSelectedIngredientsDisplay();
            this.updateSaveMealForm();
        }
    }

    updateSelectedIngredientsDisplay() {
        const container = document.getElementById('selectedIngredients');
        if (!container) return;

        if (this.selectedIngredients.length === 0) {
            container.innerHTML = `
                <div class="text-muted text-center py-4">
                    <i class="fas fa-utensils fa-3x mb-3"></i>
                    <p>No ingredients selected yet.</p>
                    <p>Select ingredients from the left panel to start building your meal.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.selectedIngredients.map(ingredient => {
            const caloriesMatch = ingredient.calories.match(/[\d.]+/);
            const caloriesValue = caloriesMatch ? parseFloat(caloriesMatch[0]) : 0;
            const adjustedCalories = (caloriesValue * ingredient.quantity / 100).toFixed(1);
            
            return `
                <div class="selected-ingredient border rounded p-3 mb-2">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1"><strong>${ingredient.name}</strong> (${ingredient.quantity}g)</h6>
                            <small class="text-muted">${ingredient.category}</small>
                            <div class="mt-2">
                                <div class="d-flex align-items-center gap-2">
                                    <label class="form-label mb-0 small">Portion (g):</label>
                                    <input type="number" class="form-control form-control-sm quantity-input" 
                                           value="${ingredient.quantity}" 
                                           data-id="${ingredient.id}"
                                           min="1" max="5000" step="1" style="width: 80px;">
                                </div>
                                <div class="mt-2">
                                    <span class="badge bg-primary">${adjustedCalories} calories</span>
                                    <small class="text-muted ms-2">(${caloriesValue} cal/100g)</small>
                                </div>
                            </div>
                        </div>
                        <button class="btn btn-sm btn-outline-danger remove-ingredient" data-id="${ingredient.id}">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }

    updateSaveMealForm() {
        const saveMealForm = document.getElementById('saveMealForm');
        const ingredientsData = document.getElementById('ingredientsData');
        
        if (this.selectedIngredients.length > 0) {
            saveMealForm.style.display = 'block';
            ingredientsData.value = JSON.stringify(this.selectedIngredients);
        } else {
            saveMealForm.style.display = 'none';
        }
    }

    async calculateNutrition() {
        if (this.selectedIngredients.length === 0) {
            this.showWarning('Please select ingredients first');
            return;
        }

        // Show loading state
        const calculateBtn = document.getElementById('calculateBtn');
        const originalContent = calculateBtn.innerHTML;
        calculateBtn.innerHTML = '<span class="loading-spinner"></span> Calculating...';
        calculateBtn.disabled = true;

        try {
            const response = await fetch('/calculate-nutrition', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ingredients: this.selectedIngredients
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.displayNutritionResults(data);
            } else {
                const error = await response.json();
                this.showError(error.error || 'Error calculating nutrition');
            }
        } catch (error) {
            console.error('Error calculating nutrition:', error);
            this.showError('Error calculating nutrition');
        } finally {
            // Restore button state
            calculateBtn.innerHTML = originalContent;
            calculateBtn.disabled = false;
        }
    }

    displayNutritionResults(data) {
        const resultsContainer = document.getElementById('nutritionResults');
        const nutritionTable = document.getElementById('nutritionTable');
        const ingredientBreakdown = document.getElementById('ingredientBreakdown');

        if (!resultsContainer || !nutritionTable || !ingredientBreakdown) return;

        // Show results container
        resultsContainer.style.display = 'block';

        // Populate nutrition table
        const nutrients = [
            { key: 'calories', name: 'Calories', unit: 'kcal' },
            { key: 'protein', name: 'Protein', unit: 'g' },
            { key: 'carbs', name: 'Carbohydrates', unit: 'g' },
            { key: 'fat', name: 'Fat', unit: 'g' },
            { key: 'fiber', name: 'Fiber', unit: 'g' },
            { key: 'sugar', name: 'Sugar', unit: 'g' },
            { key: 'sodium', name: 'Sodium', unit: 'mg' },
            { key: 'potassium', name: 'Potassium', unit: 'mg' },
            { key: 'calcium', name: 'Calcium', unit: 'mg' },
            { key: 'iron', name: 'Iron', unit: 'mg' },
            { key: 'vitamin_a', name: 'Vitamin A', unit: 'IU' },
            { key: 'vitamin_c', name: 'Vitamin C', unit: 'mg' },
            { key: 'vitamin_d', name: 'Vitamin D', unit: 'IU' },
            { key: 'vitamin_e', name: 'Vitamin E', unit: 'mg' },
            { key: 'vitamin_k', name: 'Vitamin K', unit: 'mcg' }
        ];

        nutritionTable.innerHTML = nutrients.map(nutrient => `
            <tr>
                <td><strong>${nutrient.name}</strong></td>
                <td>${data.total[nutrient.key].toFixed(2)}</td>
                <td>${nutrient.unit}</td>
            </tr>
        `).join('');

        // Create nutrition chart
        this.createNutritionChart(data.total);

        // Display ingredient breakdown
        ingredientBreakdown.innerHTML = data.ingredients.map(ingredient => `
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">${ingredient.name}</h6>
                        <p class="card-text text-muted">${ingredient.quantity}g</p>
                        <div class="row text-center">
                            <div class="col-3">
                                <small class="text-muted">Calories</small>
                                <div class="fw-bold">${ingredient.calories.toFixed(0)}</div>
                            </div>
                            <div class="col-3">
                                <small class="text-muted">Protein</small>
                                <div class="fw-bold">${ingredient.protein.toFixed(1)}g</div>
                            </div>
                            <div class="col-3">
                                <small class="text-muted">Carbs</small>
                                <div class="fw-bold">${ingredient.carbs.toFixed(1)}g</div>
                            </div>
                            <div class="col-3">
                                <small class="text-muted">Fat</small>
                                <div class="fw-bold">${ingredient.fat.toFixed(1)}g</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    createNutritionChart(nutritionData) {
        const ctx = document.getElementById('nutritionChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.nutritionChart) {
            this.nutritionChart.destroy();
        }

        // Create pie chart for macronutrients
        this.nutritionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Protein', 'Carbohydrates', 'Fat'],
                datasets: [{
                    data: [
                        nutritionData.protein * 4, // protein calories
                        nutritionData.carbs * 4,   // carb calories
                        nutritionData.fat * 9      // fat calories
                    ],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Macronutrient Distribution (Calories)',
                        color: 'var(--bs-body-color)'
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'var(--bs-body-color)'
                        }
                    }
                }
            }
        });
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showWarning(message) {
        this.showAlert(message, 'warning');
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showAlert(message, type) {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at top of main container
        const main = document.querySelector('main.container');
        if (main) {
            main.insertBefore(alert, main.firstChild);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        }
    }
}

// Initialize meal planner when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MealPlanner();
});
