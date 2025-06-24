import pandas as pd
import numpy as np
import os
import logging
from typing import Dict, List, Optional
from app import app, db
from models import Ingredient

logger = logging.getLogger(__name__)

class NutritionDataProcessor:
    """Process and normalize nutrition datasets"""
    
    def __init__(self):
        self.supported_formats = ['.xlsx', '.csv', '.json']
    
    def process_excel_file(self, file_path: str) -> pd.DataFrame:
        """Process Excel nutrition data file"""
        try:
            # Try to read Excel file
            df = pd.read_excel(file_path)
            logger.info(f"Successfully loaded Excel file with {len(df)} rows")
            return self.normalize_dataframe(df)
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            return pd.DataFrame()
    
    def process_csv_file(self, file_path: str) -> pd.DataFrame:
        """Process CSV nutrition data file"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Successfully loaded CSV file with {len(df)} rows")
            return self.normalize_dataframe(df)
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            return pd.DataFrame()
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names and data types"""
        # Common column mappings
        column_mapping = {
            'food_name': 'name',
            'food': 'name',
            'ingredient': 'name',
            'item': 'name',
            'kcal': 'calories',
            'energy': 'calories',
            'cal': 'calories',
            'proteins': 'protein',
            'carbohydrates': 'carbs',
            'carbs_g': 'carbs',
            'fats': 'fat',
            'fat_g': 'fat',
            'dietary_fiber': 'fiber',
            'fiber_g': 'fiber',
            'sugars': 'sugar',
            'sugar_g': 'sugar',
            'sodium_mg': 'sodium',
            'potassium_mg': 'potassium',
            'calcium_mg': 'calcium',
            'iron_mg': 'iron',
            'vit_a': 'vitamin_a',
            'vit_c': 'vitamin_c',
            'vit_d': 'vitamin_d',
            'vit_e': 'vitamin_e',
            'vit_k': 'vitamin_k'
        }
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
        
        # Apply column mapping
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_columns = ['name', 'calories', 'protein', 'carbs', 'fat']
        for col in required_columns:
            if col not in df.columns:
                if col == 'name':
                    logger.error("No name column found in dataset")
                    return pd.DataFrame()
                else:
                    df[col] = 0.0
        
        # Clean and convert data types
        df['name'] = df['name'].astype(str).str.strip().str.title()
        
        # Convert nutritional values to float, handling NaN
        numeric_columns = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 
                          'sodium', 'potassium', 'calcium', 'iron', 'vitamin_a', 
                          'vitamin_c', 'vitamin_d', 'vitamin_e', 'vitamin_k']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            else:
                df[col] = 0.0
        
        # Remove duplicates based on name
        df = df.drop_duplicates(subset=['name'], keep='first')
        
        # Remove rows with empty names
        df = df[df['name'].str.len() > 0]
        
        logger.info(f"Normalized dataset to {len(df)} unique ingredients")
        return df
    
    def save_to_database(self, df: pd.DataFrame) -> int:
        """Save processed data to database"""
        saved_count = 0
        
        with app.app_context():
            for _, row in df.iterrows():
                try:
                    # Check if ingredient already exists
                    existing = Ingredient.query.filter_by(name=row['name']).first()
                    
                    if not existing:
                        ingredient = Ingredient(
                            name=row['name'],
                            category=row.get('category', 'Unknown'),
                            calories=float(row.get('calories', 0)),
                            protein=float(row.get('protein', 0)),
                            carbs=float(row.get('carbs', 0)),
                            fat=float(row.get('fat', 0)),
                            fiber=float(row.get('fiber', 0)),
                            sugar=float(row.get('sugar', 0)),
                            sodium=float(row.get('sodium', 0)),
                            potassium=float(row.get('potassium', 0)),
                            calcium=float(row.get('calcium', 0)),
                            iron=float(row.get('iron', 0)),
                            vitamin_a=float(row.get('vitamin_a', 0)),
                            vitamin_c=float(row.get('vitamin_c', 0)),
                            vitamin_d=float(row.get('vitamin_d', 0)),
                            vitamin_e=float(row.get('vitamin_e', 0)),
                            vitamin_k=float(row.get('vitamin_k', 0))
                        )
                        
                        db.session.add(ingredient)
                        saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving ingredient {row.get('name', 'Unknown')}: {e}")
                    continue
            
            try:
                db.session.commit()
                logger.info(f"Successfully saved {saved_count} ingredients to database")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error committing to database: {e}")
                saved_count = 0
        
        return saved_count
    
    def process_file(self, file_path: str) -> int:
        """Process any supported file format"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return 0
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.xlsx':
            df = self.process_excel_file(file_path)
        elif file_ext == '.csv':
            df = self.process_csv_file(file_path)
        else:
            logger.error(f"Unsupported file format: {file_ext}")
            return 0
        
        if df.empty:
            logger.error("No data processed from file")
            return 0
        
        return self.save_to_database(df)

def initialize_sample_data():
    """Initialize database with sample nutrition data if empty"""
    with app.app_context():
        if Ingredient.query.count() == 0:
            processor = NutritionDataProcessor()
            sample_file = os.path.join('sample_data', 'nutrition_sample.csv')
            
            if os.path.exists(sample_file):
                count = processor.process_file(sample_file)
                logger.info(f"Initialized database with {count} sample ingredients")
            else:
                logger.warning("No sample data file found")
