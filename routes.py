from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Ingredient, Meal, MealIngredient
from data_processor import NutritionDataProcessor, initialize_sample_data
from web_scraper import NutritionScraper
import logging
import json

logger = logging.getLogger(__name__)

# Initialize sample data on startup
initialize_sample_data()

@app.route('/')
def index():
    """Home page with overview"""
    ingredient_count = Ingredient.query.count()
    return render_template('index.html', ingredient_count=ingredient_count)

@app.route('/meal-planner')
def meal_planner():
    """Meal planning interface"""
    # Get all ingredients for selection
    ingredients = Ingredient.query.order_by(Ingredient.name).all()
    categories = db.session.query(Ingredient.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('meal_planner.html', 
                         ingredients=ingredients, 
                         categories=categories)

@app.route('/search-ingredients')
def search_ingredients():
    """Search ingredients via AJAX"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    
    if not query and not category:
        ingredients = Ingredient.query.limit(20).all()
    else:
        q = Ingredient.query
        
        if query:
            q = q.filter(Ingredient.name.ilike(f'%{query}%'))
        
        if category:
            q = q.filter(Ingredient.category == category)
        
        ingredients = q.order_by(Ingredient.name).limit(50).all()
    
    return jsonify([ingredient.to_dict() for ingredient in ingredients])

@app.route('/calculate-nutrition', methods=['POST'])
def calculate_nutrition():
    """Calculate nutrition for selected ingredients"""
    try:
        data = request.get_json()
        selected_ingredients = data.get('ingredients', [])
        
        if not selected_ingredients:
            return jsonify({'error': 'No ingredients selected'}), 400
        
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'sugar': 0,
            'sodium': 0,
            'potassium': 0,
            'calcium': 0,
            'iron': 0,
            'vitamin_a': 0,
            'vitamin_c': 0,
            'vitamin_d': 0,
            'vitamin_e': 0,
            'vitamin_k': 0
        }
        
        ingredient_details = []
        
        for item in selected_ingredients:
            ingredient_id = item.get('id')
            quantity = float(item.get('quantity', 0))
            
            ingredient = Ingredient.query.get(ingredient_id)
            if ingredient and quantity > 0:
                # Calculate nutrition for this quantity (per 100g base)
                multiplier = quantity / 100.0
                
                ingredient_nutrition = {
                    'name': ingredient.name,
                    'quantity': quantity,
                    'calories': ingredient.calories * multiplier,
                    'protein': ingredient.protein * multiplier,
                    'carbs': ingredient.carbs * multiplier,
                    'fat': ingredient.fat * multiplier,
                    'fiber': ingredient.fiber * multiplier,
                    'sugar': ingredient.sugar * multiplier,
                    'sodium': ingredient.sodium * multiplier,
                    'potassium': ingredient.potassium * multiplier,
                    'calcium': ingredient.calcium * multiplier,
                    'iron': ingredient.iron * multiplier,
                    'vitamin_a': ingredient.vitamin_a * multiplier,
                    'vitamin_c': ingredient.vitamin_c * multiplier,
                    'vitamin_d': ingredient.vitamin_d * multiplier,
                    'vitamin_e': ingredient.vitamin_e * multiplier,
                    'vitamin_k': ingredient.vitamin_k * multiplier
                }
                
                ingredient_details.append(ingredient_nutrition)
                
                # Add to totals
                for key in total_nutrition:
                    if key in ingredient_nutrition:
                        total_nutrition[key] += ingredient_nutrition[key]
        
        return jsonify({
            'total': total_nutrition,
            'ingredients': ingredient_details
        })
        
    except Exception as e:
        logger.error(f"Error calculating nutrition: {e}")
        return jsonify({'error': 'Error calculating nutrition'}), 500

@app.route('/save-meal', methods=['POST'])
def save_meal():
    """Save a meal with selected ingredients"""
    try:
        meal_name = request.form.get('meal_name')
        meal_description = request.form.get('meal_description', '')
        ingredients_data = request.form.get('ingredients_data')
        
        if not meal_name or not ingredients_data:
            flash('Meal name and ingredients are required', 'error')
            return redirect(url_for('meal_planner'))
        
        ingredients = json.loads(ingredients_data)
        
        # Create new meal
        meal = Meal(name=meal_name, description=meal_description)
        db.session.add(meal)
        db.session.flush()  # Get the meal ID
        
        # Add ingredients to meal
        for item in ingredients:
            meal_ingredient = MealIngredient(
                meal_id=meal.id,
                ingredient_id=item['id'],
                quantity=item['quantity']
            )
            db.session.add(meal_ingredient)
        
        db.session.commit()
        flash(f'Meal "{meal_name}" saved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving meal: {e}")
        flash('Error saving meal', 'error')
    
    return redirect(url_for('meal_planner'))

@app.route('/upload-data', methods=['POST'])
def upload_data():
    """Upload and process nutrition dataset"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file:
        try:
            # Save uploaded file temporarily
            filename = file.filename
            file_path = f'/tmp/{filename}'
            file.save(file_path)
            
            # Process the file
            processor = NutritionDataProcessor()
            count = processor.process_file(file_path)
            
            if count > 0:
                flash(f'Successfully processed {count} ingredients from {filename}', 'success')
            else:
                flash('No data was processed from the file', 'error')
            
        except Exception as e:
            logger.error(f"Error processing uploaded file: {e}")
            flash('Error processing file', 'error')
    
    return redirect(url_for('index'))

@app.route('/scrape-ingredient', methods=['POST'])
def scrape_ingredient():
    """Scrape nutrition data for a specific ingredient"""
    ingredient_name = request.form.get('ingredient_name', '').strip()
    
    if not ingredient_name:
        flash('Ingredient name is required', 'error')
        return redirect(url_for('meal_planner'))
    
    try:
        scraper = NutritionScraper()
        success = scraper.scrape_and_save_ingredient(ingredient_name)
        
        if success:
            flash(f'Successfully scraped nutrition data for {ingredient_name}', 'success')
        else:
            flash(f'Could not find nutrition data for {ingredient_name}. You can add it manually below.', 'warning')
            
    except Exception as e:
        logger.error(f"Error scraping ingredient {ingredient_name}: {e}")
        flash('Error scraping ingredient data', 'error')
    
    return redirect(url_for('meal_planner'))

@app.route('/add-manual-ingredient', methods=['POST'])
def add_manual_ingredient():
    """Add ingredient with manual nutrition data"""
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        calories = float(request.form.get('calories', 0))
        protein = float(request.form.get('protein', 0))
        carbs = float(request.form.get('carbs', 0))
        fat = float(request.form.get('fat', 0))
        fiber = float(request.form.get('fiber', 0))
        sugar = float(request.form.get('sugar', 0))
        sodium = float(request.form.get('sodium', 0))
        potassium = float(request.form.get('potassium', 0))
        calcium = float(request.form.get('calcium', 0))
        iron = float(request.form.get('iron', 0))
        vitamin_a = float(request.form.get('vitamin_a', 0))
        vitamin_c = float(request.form.get('vitamin_c', 0))
        vitamin_d = float(request.form.get('vitamin_d', 0))
        vitamin_e = float(request.form.get('vitamin_e', 0))
        vitamin_k = float(request.form.get('vitamin_k', 0))
        
        if not name:
            flash('Ingredient name is required', 'error')
            return redirect(url_for('meal_planner'))
        
        # Check if ingredient already exists
        existing = Ingredient.query.filter_by(name=name).first()
        if existing:
            flash(f'Ingredient "{name}" already exists in database', 'warning')
            return redirect(url_for('meal_planner'))
        
        # Create new ingredient
        ingredient = Ingredient(
            name=name,
            category=category or 'User Added',
            calories=calories,
            protein=protein,
            carbs=carbs,
            fat=fat,
            fiber=fiber,
            sugar=sugar,
            sodium=sodium,
            potassium=potassium,
            calcium=calcium,
            iron=iron,
            vitamin_a=vitamin_a,
            vitamin_c=vitamin_c,
            vitamin_d=vitamin_d,
            vitamin_e=vitamin_e,
            vitamin_k=vitamin_k
        )
        
        db.session.add(ingredient)
        db.session.commit()
        
        flash(f'Successfully added "{name}" to the database', 'success')
        
    except ValueError as e:
        flash('Please enter valid numbers for nutritional values', 'error')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding manual ingredient: {e}")
        flash('Error adding ingredient to database', 'error')
    
    return redirect(url_for('meal_planner'))

@app.route('/results')
def results():
    """Display nutrition calculation results"""
    # This route would typically receive data via session or parameters
    # For now, redirect to meal planner
    return redirect(url_for('meal_planner'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('base.html'), 500
