#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "======================================="
echo "  Fitness Tracker Application Setup  "
echo "======================================="

# Set FLASK_APP environment variable for Flask CLI commands
export FLASK_APP=app.py

# Create data directory if it doesn't exist (db is stored in data/fitness_tracker.db)
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
fi

echo "\n---> Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt --quiet
echo "Dependencies installed successfully."

echo "\n---> Initializing the database..."
flask init-db
echo "Database initialized successfully."

echo "\n---> Starting the Flask application..."
echo "Application will be available at http://0.0.0.0:9000"
python app.py

echo "\nApplication startup process finished."
