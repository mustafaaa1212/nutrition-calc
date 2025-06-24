#!/bin/bash
# Build script for Render deployment

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up database..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

echo "Build completed successfully!"