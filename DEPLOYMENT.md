# Render Deployment Guide

## Quick Deploy to Render

1. **Push your code to GitHub** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Nutrition Calculator"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: nutrition-calculator
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
     - **Instance Type**: Free tier

3. **Add Environment Variables**
   - `SESSION_SECRET`: Generate a random string (Render can auto-generate)
   - `DATABASE_URL`: Will be automatically set when you add a database

4. **Add PostgreSQL Database**
   - In Render dashboard, click "New +" → "PostgreSQL"
   - **Name**: nutrition-db
   - **Database**: nutrition_calculator
   - **User**: nutrition_user
   - **Region**: Same as your web service
   - **Plan**: Free tier

5. **Connect Database to Web Service**
   - In your web service settings, go to "Environment"
   - Add `DATABASE_URL` variable
   - Select "From Database" and choose your PostgreSQL database

## Alternative: One-Click Deploy

You can also use the `render.yaml` file included in this project for one-click deployment:

1. In Render dashboard, click "New +" → "Blueprint"
2. Connect your GitHub repository
3. Render will automatically read the `render.yaml` file and set up both the web service and database

## Post-Deployment

After successful deployment:
- Your app will be available at `https://your-app-name.onrender.com`
- The database will be automatically created with all necessary tables
- You can upload nutrition datasets through the web interface
- The app supports both SQLite (development) and PostgreSQL (production)

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (auto-set by Render)
- `SESSION_SECRET`: Secret key for Flask sessions
- `PORT`: Port number (auto-set by Render)

## Files Added for Deployment

- `requirements.txt`: Python dependencies
- `render.yaml`: Blueprint for one-click deployment
- `runtime.txt`: Python version specification
- `build.sh`: Build script for database setup
- Updated `app.py`: Database URL handling for PostgreSQL
- Updated `main.py`: Port configuration for Render

Your nutrition calculator is now ready for production deployment on Render!