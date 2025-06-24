from app import db
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    
    # Nutritional values per 100g
    calories = Column(Float, default=0.0)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fat = Column(Float, default=0.0)
    fiber = Column(Float, default=0.0)
    sugar = Column(Float, default=0.0)
    sodium = Column(Float, default=0.0)
    potassium = Column(Float, default=0.0)
    calcium = Column(Float, default=0.0)
    iron = Column(Float, default=0.0)
    vitamin_a = Column(Float, default=0.0)
    vitamin_c = Column(Float, default=0.0)
    vitamin_d = Column(Float, default=0.0)
    vitamin_e = Column(Float, default=0.0)
    vitamin_k = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Ingredient {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'fiber': self.fiber,
            'sugar': self.sugar,
            'sodium': self.sodium,
            'potassium': self.potassium,
            'calcium': self.calcium,
            'iron': self.iron,
            'vitamin_a': self.vitamin_a,
            'vitamin_c': self.vitamin_c,
            'vitamin_d': self.vitamin_d,
            'vitamin_e': self.vitamin_e,
            'vitamin_k': self.vitamin_k
        }

class Meal(db.Model):
    __tablename__ = 'meals'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to meal ingredients
    meal_ingredients = relationship("MealIngredient", back_populates="meal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Meal {self.name}>'

class MealIngredient(db.Model):
    __tablename__ = 'meal_ingredients'
    
    id = Column(Integer, primary_key=True)
    meal_id = Column(Integer, ForeignKey('meals.id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    quantity = Column(Float, nullable=False)  # in grams
    
    # Relationships
    meal = relationship("Meal", back_populates="meal_ingredients")
    ingredient = relationship("Ingredient")
    
    def __repr__(self):
        return f'<MealIngredient {self.ingredient.name}: {self.quantity}g>'
