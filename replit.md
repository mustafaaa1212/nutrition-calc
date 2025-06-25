# Nutrition Calculator - Replit.md

## Overview

This is a Flask-based web application for nutrition calculation and meal planning. Users can search through a comprehensive ingredient database, add ingredients to meal plans with custom quantities, and get detailed nutritional breakdowns. The application features a clean, modern interface with Bootstrap theming and real-time calculations.

## System Architecture

The application follows a traditional MVC pattern with Flask as the web framework:

- **Frontend**: HTML templates with Bootstrap styling, JavaScript for interactive features
- **Backend**: Flask web application with SQLAlchemy ORM
- **Database**: SQLite (default) with PostgreSQL support via environment configuration
- **Data Processing**: Pandas for CSV/Excel data import and normalization
- **Web Scraping**: Trafilatura for extracting nutrition data from web sources

## Key Components

### 1. Application Structure
- `app.py`: Flask application factory with database initialization
- `main.py`: Application entry point for development server
- `models.py`: SQLAlchemy database models
- `routes.py`: Web route handlers and API endpoints
- `data_processor.py`: Data import and normalization utilities
- `web_scraper.py`: Web scraping functionality for nutrition data

### 2. Database Models
- **Ingredient**: Core model storing nutritional information per 100g including:
  - Basic info: name, category
  - Macronutrients: calories, protein, carbs, fat, fiber, sugar
  - Micronutrients: vitamins (A, C, D, E, K), minerals (sodium, potassium, calcium, iron)
- **Meal**: Planned meal combinations (model referenced but not fully implemented)
- **MealIngredient**: Junction table for meal-ingredient relationships

### 3. Frontend Components
- **Base Template**: Bootstrap-based layout with dark theme
- **Index Page**: Landing page with feature overview
- **Meal Planner**: Interactive ingredient selection and meal planning interface
- **Results Page**: Nutritional analysis display with charts

### 4. Data Management
- **Sample Data**: CSV file with common ingredients and nutritional values
- **Data Processor**: Handles Excel/CSV import with column mapping and normalization
- **Web Scraper**: Extracts nutrition data from online sources (USDA FoodData Central)

## Data Flow

1. **Ingredient Search**: Users search/filter ingredients via AJAX requests
2. **Meal Building**: Selected ingredients are added to meal plan with quantities
3. **Calculation**: JavaScript calculates nutritional totals in real-time
4. **Visualization**: Charts display nutritional breakdown and analysis
5. **Persistence**: Meals can be saved to database for future reference

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **Pandas**: Data processing and CSV/Excel handling
- **NumPy**: Numerical computations
- **Requests**: HTTP client for web scraping
- **Trafilatura**: Web content extraction
- **Gunicorn**: Production WSGI server
- **psycopg2-binary**: PostgreSQL database adapter

### Frontend Libraries
- **Bootstrap**: UI framework with dark theme
- **Chart.js**: Data visualization and charts
- **Font Awesome**: Icon library
- **jQuery**: DOM manipulation (implicit dependency)

## Deployment Strategy

### Development
- Flask development server on port 5000
- SQLite database for local development
- Debug mode enabled with hot reloading

### Production
- Gunicorn WSGI server with autoscaling deployment target
- PostgreSQL database via DATABASE_URL environment variable
- Connection pooling with pre-ping health checks
- ProxyFix middleware for proper header handling

### Configuration
- Environment-based configuration (DATABASE_URL, SESSION_SECRET)
- Nix package management for system dependencies
- UV lock file for Python dependency management

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Recent updates:
- June 24, 2025: Enhanced meal planner with manual ingredient addition
- Added comprehensive nutrition entry form with organized field categories
- Implemented backend route for manual ingredient submission
- Fixed form duplication issues for cleaner user interface
- Cleaned up meal planner template to have single manual entry section
- Added portion size functionality with gram-based calculations
- Enhanced calculator to handle custom portion sizes for accurate nutrition
- Updated UI to show portion inputs and adjusted calorie displays
- Implemented duplicate ingredient prevention with clear visual feedback
- Added proper requirements.txt file for Render deployment
- Enhanced deployment configuration with production optimizations
- Configured PostgreSQL support for production deployment

## Deployment

The application is ready for deployment on Render with:
- PostgreSQL database support
- Environment variable configuration
- Production-ready gunicorn server
- One-click deployment via render.yaml blueprint