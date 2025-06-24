import trafilatura
import requests
import logging
from typing import Dict, List, Optional
import re
from app import app, db
from models import Ingredient

logger = logging.getLogger(__name__)

class NutritionScraper:
    """Scrape nutrition data from various online sources"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_website_text_content(self, url: str) -> str:
        """
        Extract main text content from a website using trafilatura
        """
        try:
            # Fetch the URL content
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                # Extract text content
                text = trafilatura.extract(downloaded)
                return text if text else ""
            return ""
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return ""
    
    def scrape_usda_nutrition(self, ingredient_name: str) -> Optional[Dict]:
        """
        Scrape nutrition data from USDA FoodData Central
        Note: This is a simplified example - in production, you'd use their API
        """
        try:
            # Format ingredient name for search
            formatted_name = ingredient_name.replace(' ', '+')
            search_url = f"https://fdc.nal.usda.gov/fdc-app.html#/?query={formatted_name}"
            
            # Get text content
            content = self.get_website_text_content(search_url)
            
            if content:
                # Extract nutritional information using regex patterns
                nutrition_data = self._extract_nutrition_from_text(content, ingredient_name)
                return nutrition_data
            
        except Exception as e:
            logger.error(f"Error scraping USDA data for {ingredient_name}: {e}")
        
        return None
    
    def scrape_nutrition_gov(self, ingredient_name: str) -> Optional[Dict]:
        """
        Scrape nutrition data from nutrition.gov
        """
        try:
            formatted_name = ingredient_name.replace(' ', '%20')
            search_url = f"https://www.nutrition.gov/search?query={formatted_name}"
            
            content = self.get_website_text_content(search_url)
            
            if content:
                nutrition_data = self._extract_nutrition_from_text(content, ingredient_name)
                return nutrition_data
                
        except Exception as e:
            logger.error(f"Error scraping nutrition.gov data for {ingredient_name}: {e}")
        
        return None
    
    def _extract_nutrition_from_text(self, text: str, ingredient_name: str) -> Dict:
        """
        Extract nutrition values from scraped text using regex patterns
        """
        nutrition_data = {
            'name': ingredient_name,
            'calories': 0.0,
            'protein': 0.0,
            'carbs': 0.0,
            'fat': 0.0,
            'fiber': 0.0,
            'sugar': 0.0,
            'sodium': 0.0,
            'potassium': 0.0,
            'calcium': 0.0,
            'iron': 0.0,
            'vitamin_a': 0.0,
            'vitamin_c': 0.0
        }
        
        # Regex patterns for extracting nutrition values
        patterns = {
            'calories': r'(?:calories?|kcal|energy)[\s:]*(\d+(?:\.\d+)?)',
            'protein': r'protein[\s:]*(\d+(?:\.\d+)?)',
            'carbs': r'(?:carbohydrates?|carbs?)[\s:]*(\d+(?:\.\d+)?)',
            'fat': r'(?:total\s+)?fat[\s:]*(\d+(?:\.\d+)?)',
            'fiber': r'(?:dietary\s+)?fiber[\s:]*(\d+(?:\.\d+)?)',
            'sugar': r'(?:total\s+)?sugars?[\s:]*(\d+(?:\.\d+)?)',
            'sodium': r'sodium[\s:]*(\d+(?:\.\d+)?)',
            'potassium': r'potassium[\s:]*(\d+(?:\.\d+)?)',
            'calcium': r'calcium[\s:]*(\d+(?:\.\d+)?)',
            'iron': r'iron[\s:]*(\d+(?:\.\d+)?)',
            'vitamin_a': r'vitamin\s+a[\s:]*(\d+(?:\.\d+)?)',
            'vitamin_c': r'vitamin\s+c[\s:]*(\d+(?:\.\d+)?)'
        }
        
        text_lower = text.lower()
        
        for nutrient, pattern in patterns.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                try:
                    # Take the first match and convert to float
                    nutrition_data[nutrient] = float(matches[0])
                except (ValueError, IndexError):
                    continue
        
        return nutrition_data
    
    def scrape_and_save_ingredient(self, ingredient_name: str) -> bool:
        """
        Scrape nutrition data for an ingredient and save to database
        """
        try:
            # Try multiple sources
            nutrition_data = self.scrape_usda_nutrition(ingredient_name)
            
            if not nutrition_data or nutrition_data['calories'] == 0:
                nutrition_data = self.scrape_nutrition_gov(ingredient_name)
            
            if nutrition_data and nutrition_data['calories'] > 0:
                with app.app_context():
                    # Check if ingredient already exists
                    existing = Ingredient.query.filter_by(name=ingredient_name).first()
                    
                    if not existing:
                        ingredient = Ingredient(
                            name=nutrition_data['name'],
                            calories=nutrition_data['calories'],
                            protein=nutrition_data['protein'],
                            carbs=nutrition_data['carbs'],
                            fat=nutrition_data['fat'],
                            fiber=nutrition_data['fiber'],
                            sugar=nutrition_data['sugar'],
                            sodium=nutrition_data['sodium'],
                            potassium=nutrition_data['potassium'],
                            calcium=nutrition_data['calcium'],
                            iron=nutrition_data['iron'],
                            vitamin_a=nutrition_data['vitamin_a'],
                            vitamin_c=nutrition_data['vitamin_c']
                        )
                        
                        db.session.add(ingredient)
                        db.session.commit()
                        
                        logger.info(f"Successfully scraped and saved {ingredient_name}")
                        return True
                    
        except Exception as e:
            logger.error(f"Error in scrape_and_save_ingredient for {ingredient_name}: {e}")
        
        return False

def scrape_missing_ingredients(ingredient_names: List[str]) -> int:
    """
    Scrape nutrition data for a list of missing ingredients
    """
    scraper = NutritionScraper()
    success_count = 0
    
    for name in ingredient_names:
        if scraper.scrape_and_save_ingredient(name):
            success_count += 1
    
    return success_count
