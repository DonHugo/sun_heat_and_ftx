#!/bin/bash
# Solar Heating Local GUI Startup Script

echo "🌐 Starting Solar Heating Local GUI..."

# Change to the web interface directory
cd /home/pi/solar_heating/python/v3/web_interface

# Activate virtual environment if it exists
if [ -f "/home/pi/solar_heating/.venv/bin/activate" ]; then
    source /home/pi/solar_heating/.venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Install requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Requirements installed"
fi

# Start the Flask application
echo "🚀 Starting web server on http://0.0.0.0:5000"
python3 app.py
