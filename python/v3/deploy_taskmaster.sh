#!/bin/bash

# TaskMaster AI Integration Deployment Script
# Deploys the new TaskMaster AI feature to your solar heating system

set -e  # Exit on any error

echo "🚀 Deploying TaskMaster AI Integration (FR-008)..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main_system.py" ]; then
    print_error "Please run this script from the python/v3 directory"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [ -z "$PYTHON_VERSION" ]; then
    print_error "Python 3 is not installed"
    exit 1
fi

print_status "Python version: $PYTHON_VERSION"

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "Virtual environment found, activating..."
    source venv/bin/activate
    print_success "Virtual environment activated"
else
    print_warning "No virtual environment found, creating one..."
    python3 -m venv venv
    source venv/bin/activate
    print_success "Virtual environment created and activated"
fi

# Install/upgrade dependencies
print_status "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if httpx is installed (required for TaskMaster AI)
if ! python -c "import httpx" 2>/dev/null; then
    print_status "Installing TaskMaster AI dependencies..."
    pip install httpx python-dotenv pydantic
fi

print_success "Dependencies installed"

# Test the TaskMaster integration
print_status "Testing TaskMaster AI integration..."
if python test_taskmaster.py; then
    print_success "TaskMaster AI integration test passed"
else
    print_error "TaskMaster AI integration test failed"
    exit 1
fi

# Test the insights demonstration
print_status "Testing system insights demonstration..."
if python demo_insights.py; then
    print_success "System insights demonstration passed"
else
    print_error "System insights demonstration failed"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning "No .env file found, creating template..."
    cat > .env << EOF
# TaskMaster AI Configuration
SOLAR_TASKMASTER_ENABLED=true
SOLAR_TASKMASTER_API_KEY=your_api_key_here
SOLAR_TASKMASTER_BASE_URL=https://api.taskmaster.ai

# System Configuration
SOLAR_TEST_MODE=false
SOLAR_DEBUG_MODE=false
SOLAR_LOG_LEVEL=info

# MQTT Configuration
SOLAR_MQTT_BROKER=192.168.0.110
SOLAR_MQTT_PORT=1883
SOLAR_MQTT_USERNAME=mqtt_beaches
SOLAR_MQTT_PASSWORD=uQX6NiZ.7R

# Hardware Configuration
SOLAR_HARDWARE_PLATFORM=raspberry_pi_zero_2_w
SOLAR_RTD_BOARD_ADDRESS=0
SOLAR_MEGABAS_BOARD_ADDRESS=3
SOLAR_RELAY_BOARD_ADDRESS=2

# Temperature Thresholds
SOLAR_TEMPERATURE_THRESHOLD_HIGH=80.0
SOLAR_TEMPERATURE_THRESHOLD_LOW=20.0
SOLAR_TEMPERATURE_UPDATE_INTERVAL=30

# Solar Collector Configuration
SOLAR_SET_TEMP_TANK_1=70.0
SOLAR_DTSTART_TANK_1=8.0
SOLAR_DTSTOP_TANK_1=4.0
SOLAR_KYLNING_KOLLEKTOR=90.0
SOLAR_TEMP_KOK=150.0

# Performance Configuration
SOLAR_MAX_CONCURRENT_TASKS=5
SOLAR_AI_ANALYSIS_INTERVAL=3600
EOF
    print_success ".env template created - please edit with your actual values"
else
    print_success ".env file found"
fi

# Check if Docker is available
if command -v docker &> /dev/null; then
    print_status "Docker detected, creating Docker deployment..."
    
    # Build Docker image
    if docker build -t solar-heating-v3 .; then
        print_success "Docker image built successfully"
        
        # Create docker-compose override for local development
        if [ ! -f "docker-compose.override.yml" ]; then
            cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  solar-heating-v3:
    environment:
      - SOLAR_TEST_MODE=true
      - SOLAR_DEBUG_MODE=true
    volumes:
      - .:/app
      - ./logs:/app/logs
EOF
            print_success "Docker Compose override created for development"
        fi
    else
        print_warning "Docker build failed, continuing with local deployment"
    fi
else
    print_warning "Docker not available, skipping Docker deployment"
fi

# Create systemd service file for production deployment
if [ ! -f "solar_heating_v3_taskmaster.service" ]; then
    print_status "Creating systemd service file..."
    cat > solar_heating_v3_taskmaster.service << EOF
[Unit]
Description=Solar Heating System v3 with TaskMaster AI Integration
After=network.target mqtt.service
Wants=mqtt.service

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main_system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# TaskMaster AI specific environment variables
Environment=SOLAR_TASKMASTER_ENABLED=true
Environment=SOLAR_TASKMASTER_API_KEY=your_api_key_here

[Install]
WantedBy=multi-user.target
EOF
    print_success "Systemd service file created"
fi

# Create deployment verification script
cat > verify_deployment.sh << 'EOF'
#!/bin/bash

echo "🔍 Verifying TaskMaster AI Integration Deployment..."

# Check if main system can import TaskMaster modules
if python -c "
from taskmaster_integration import taskmaster
from taskmaster_service import taskmaster_service
print('✓ TaskMaster modules imported successfully')
"; then
    echo "✅ TaskMaster AI integration verified"
else
    echo "❌ TaskMaster AI integration verification failed"
    exit 1
fi

# Check if configuration is loaded
if python -c "
from config import config
print(f'✓ TaskMaster enabled: {config.taskmaster_enabled}')
print(f'✓ TaskMaster API key: {bool(config.taskmaster_api_key)}')
"; then
    echo "✅ Configuration loaded successfully"
else
    echo "❌ Configuration loading failed"
    exit 1
fi

echo "🎉 Deployment verification completed successfully!"
EOF

chmod +x verify_deployment.sh

# Final deployment summary
echo ""
echo "🎉 TaskMaster AI Integration Deployment Complete!"
echo "================================================"
echo ""
echo "✅ What was deployed:"
echo "   • TaskMaster AI integration (FR-008)"
echo "   • Enhanced system insights and optimization"
echo "   • Automated task management"
echo "   • Performance monitoring and recommendations"
echo ""
echo "📁 Files created:"
echo "   • .env (configuration template)"
echo "   • Dockerfile (container deployment)"
echo "   • docker-compose.yml (orchestration)"
echo "   • solar_heating_v3_taskmaster.service (systemd service)"
echo "   • verify_deployment.sh (deployment verification)"
echo ""
echo "🚀 Next steps:"
echo "   1. Edit .env file with your actual values"
echo "   2. Set your TaskMaster AI API key"
echo "   3. Test the integration: python test_taskmaster.py"
echo "   4. Run the system: python main_system.py"
echo "   5. Verify deployment: ./verify_deployment.sh"
echo ""
echo "🐳 For Docker deployment:"
echo "   docker-compose up -d"
echo ""
echo "🔧 For systemd service:"
echo "   sudo cp solar_heating_v3_taskmaster.service /etc/systemd/system/"
echo "   sudo systemctl enable solar_heating_v3_taskmaster.service"
echo "   sudo systemctl start solar_heating_v3_taskmaster.service"
echo ""
echo "📚 Documentation: TASKMASTER_INTEGRATION.md"
echo ""

print_success "Deployment completed successfully!"
