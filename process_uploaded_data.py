#!/usr/bin/env python3
"""
Process the uploaded nutrition dataset and add it to the database
"""

import pandas as pd
import numpy as np
import os
import sys
import logging

# Set up a simple app context without circular imports
import sqlite3
from datetime import datetime

def process_excel_file(file_path: str):
    """Process Excel nutrition data file"""
    try:
        df = pd.read_excel(file_path)
        print(f"Successfully loaded Excel file with {len(df)} rows")
        return normalize_dataframe(df)
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return pd.DataFrame()

def normalize_dataframe(df: pd.DataFrame):
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
                print("No name column found in dataset")
                return pd.DataFrame()
            else:
                df[col] = 0.0
    
    # Clean and convert data types
    df['name'] = df['name'].astype(str).str.strip().str.title()
    
    # Convert nutritional values to float
    numeric_columns = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 
                      'sodium', 'potassium', 'calcium', 'iron', 'vitamin_a', 
                      'vitamin_c', 'vitamin_d', 'vitamin_e', 'vitamin_k']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        else:
            df[col] = 0.0
    
    # Remove duplicates and empty names
    df = df.drop_duplicates(subset=['name'], keep='first')
    df = df[df['name'].str.len() > 0]
    
    print(f"Normalized dataset to {len(df)} unique ingredients")
    return df

def save_to_database(df: pd.DataFrame):
    """Save processed data to SQLite database"""
    saved_count = 0
    
    # Connect to database
    conn = sqlite3.connect('nutrition.db')
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        try:
            # Check if ingredient already exists
            cursor.execute("SELECT id FROM ingredients WHERE name = ?", (row['name'],))
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute("""
                    INSERT INTO ingredients (
                        name, category, calories, protein, carbs, fat, fiber, sugar,
                        sodium, potassium, calcium, iron, vitamin_a, vitamin_c,
                        vitamin_d, vitamin_e, vitamin_k, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['name'],
                    row.get('category', 'Unknown'),
                    float(row.get('calories', 0)),
                    float(row.get('protein', 0)),
                    float(row.get('carbs', 0)),
                    float(row.get('fat', 0)),
                    float(row.get('fiber', 0)),
                    float(row.get('sugar', 0)),
                    float(row.get('sodium', 0)),
                    float(row.get('potassium', 0)),
                    float(row.get('calcium', 0)),
                    float(row.get('iron', 0)),
                    float(row.get('vitamin_a', 0)),
                    float(row.get('vitamin_c', 0)),
                    float(row.get('vitamin_d', 0)),
                    float(row.get('vitamin_e', 0)),
                    float(row.get('vitamin_k', 0)),
                    datetime.utcnow().isoformat()
                ))
                saved_count += 1
                
        except Exception as e:
            print(f"Error saving ingredient {row.get('name', 'Unknown')}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    print(f"Successfully saved {saved_count} ingredients to database")
    return saved_count

def main():
    data_file = 'attached_assets/nutrition_1750793059931.xlsx'
    
    if not os.path.exists(data_file):
        print(f"Error: Data file {data_file} not found")
        return 1
    
    print(f"Processing nutrition data from {data_file}...")
    
    # Process the Excel file
    df = process_excel_file(data_file)
    
    if df.empty:
        print("No data processed from file")
        return 1
    
    # Save to database
    count = save_to_database(df)
    
    if count > 0:
        print("The new ingredients are now available in your meal planner!")
    else:
        print("No new ingredients were added. They may already exist in the database.")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())