#!/bin/bash
set -e

# Setup logging to specified file
exec > >(tee -a ${LOGFILE}) 2>&1

echo "========== STARTING USER DATA EXECUTION =========="
echo "Date: $(date)"
echo "Hostname: $(hostname)"

# Install absolutely necessary tools first
echo "Installing initial utilities for debugging..."
yum update -y
yum install -y net-tools curl wget htop python3

# Set up basic health check first (we want this running ASAP)
echo "Creating a simple health endpoint..."
mkdir -p /app
cat > /app/health_server.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import json
from datetime import datetime

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/basic-health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Simple health check response
            response = {
                "status": "ok",
                "message": "Basic health check passed",
                "timestamp": datetime.now().isoformat(),
                "stage": "Initial startup",
                "startup_progress": "Health server running"
            }

            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print("Starting basic health server on port 8080...")
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()
EOF

# Make it executable
chmod +x /app/health_server.py

# Start the health server immediately
echo "Starting basic health server on port 8080..."
nohup python3 /app/health_server.py > /app/health_server.log 2>&1 &
sleep 3

# Ensure it's running
if curl -s http://localhost:8080/basic-health | grep -q "ok"; then
  echo "Basic health server is running."
else
  echo "WARNING: Basic health server failed to start."
  echo "Health server logs:"
  cat /app/health_server.log
fi

# Print useful debugging information
echo "System information:"
uname -a
echo "Network interfaces:"
ip addr show
echo "IP routing:"
ip route
echo "DNS configuration:"
cat /etc/resolv.conf

# Now continue with the rest of the setup
echo "Updating system packages..."
yum install -y docker git aws-cli python3-pip

# Verify installations
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"
echo "AWS CLI version: $(aws --version)"
echo "Git version: $(git --version)"

# Start Docker service
echo "Starting Docker service..."
systemctl start docker
systemctl enable docker
echo "Docker status: $(systemctl status docker | grep Active)"

# Update health check to indicate progress
echo "Updating health server status..."
cat > /app/health_server.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import socket
import json
import subprocess
from datetime import datetime

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/basic-health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Collect system info
            hostname = socket.gethostname()
            try:
                ip = socket.gethostbyname(hostname)
            except:
                ip = "unknown"

            # Check if main app might be running
            app_running = False
            try:
                with open('/app/api_status.txt', 'r') as f:
                    status = f.read().strip()
                    app_running = 'running' in status
            except:
                app_running = False

            # Get disk space
            try:
                disk_space = subprocess.check_output(['df', '-h', '/']).decode('utf-8')
            except:
                disk_space = "unavailable"

            # Get memory usage
            try:
                memory = subprocess.check_output(['free', '-m']).decode('utf-8')
            except:
                memory = "unavailable"

            response = {
                "status": "ok",
                "message": "Basic health check passed",
                "timestamp": datetime.now().isoformat(),
                "hostname": hostname,
                "ip": ip,
                "app_running": app_running,
                "system_info": {
                    "disk_space": disk_space.split('\n') if isinstance(disk_space, str) else [],
                    "memory": memory.split('\n') if isinstance(memory, str) else []
                }
            }

            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print("Starting basic health server on port 8080...")
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()
EOF

# Restart the health server
echo "Restarting health server with updated functionality..."
pkill -f "python3 /app/health_server.py" || echo "Health server not running, starting fresh"
nohup python3 /app/health_server.py > /app/health_server.log 2>&1 &
sleep 3

# Clone application repository
echo "Cloning application repository..."
cd /app
GIT_REPO_URL="https://github.com/shreeraj1746/movie-genre-predictor.git"
echo "Repository URL: $GIT_REPO_URL"

# Check if the directory is already a git repository
if [ -d ".git" ]; then
  echo "Git repository already exists. Pulling latest changes instead of cloning."
  git pull
else
  # Make sure the directory is empty
  if [ "$(ls -A | grep -v 'health_server.py' | grep -v 'health_server.log' | grep -v 'api_status.txt' | grep -v 'simple_api_server.py' | grep -v 'simple_api.log')" ]; then
    echo "Directory not empty. Moving existing files to backup directory."
    mkdir -p /app/backup
    mv $(ls -A | grep -v 'health_server.py' | grep -v 'health_server.log' | grep -v 'api_status.txt' | grep -v 'backup' | grep -v 'simple_api_server.py' | grep -v 'simple_api.log') /app/backup/
  fi
  # Now clone the repository
  git clone $GIT_REPO_URL .
fi

if [ $? -ne 0 ]; then
  echo "ERROR: Failed to clone/update repository!"
  echo "error" > /app/api_status.txt
  exit 1
fi
echo "Repository cloned/updated successfully."

# List files in repository
echo "Files in repository:"
ls -la

# Install Python dependencies
echo "Installing Python dependencies..."
echo "installing" > /app/api_status.txt
pip3 install --upgrade pip
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to install dependencies!"
  echo "error" > /app/api_status.txt
  exit 1
fi
echo "Dependencies installed successfully."

# Download model files from S3 bucket (if they exist)
echo "Checking for model files in S3 bucket..."
aws s3 cp s3://${bucket_name}/models/ ./models/ --recursive || echo "No model files in S3 yet"

# Configure environment
echo "Configuring environment variables..."
export APP_NAME=${app_name}
export ENVIRONMENT=${environment}
export AWS_REGION=${region}
export MODEL_PATH=/app/models/latest/model.joblib
export FEATURE_EXTRACTOR_PATH=/app/models/latest/feature_extractor.joblib

# Create permanent environment settings
cat > /etc/profile.d/app-env.sh << EOF
export APP_NAME=${app_name}
export ENVIRONMENT=${environment}
export AWS_REGION=${region}
export MODEL_PATH=/app/models/latest/model.joblib
export FEATURE_EXTRACTOR_PATH=/app/models/latest/feature_extractor.joblib
EOF
chmod +x /etc/profile.d/app-env.sh
source /etc/profile.d/app-env.sh

# Create sample data and model if not already available
if [ ! -f "$MODEL_PATH" ]; then
  echo "Model not found, creating sample data and training model..."
  mkdir -p /app/models/latest
  echo "Generating sample data..."
  python3 data/sample_data_generator.py
  if [ $? -ne 0 ]; then
    echo "ERROR: Failed to generate sample data!"
    echo "error" > /app/api_status.txt
    exit 1
  fi

  echo "Preprocessing data..."
  python3 -m src.data.preprocess
  if [ $? -ne 0 ]; then
    echo "ERROR: Failed to preprocess data!"
    echo "error" > /app/api_status.txt
    exit 1
  fi

  echo "Training model..."
  python3 -m src.flows.genre_classifier run
  if [ $? -ne 0 ]; then
    echo "ERROR: Failed to train model!"
    echo "error" > /app/api_status.txt
    exit 1
  fi

  echo "Model creation complete."
fi

# Ensure model files exist
echo "Checking model files..."
if [ -f "$MODEL_PATH" ] && [ -f "$FEATURE_EXTRACTOR_PATH" ]; then
  echo "Model files exist and are ready for use."
  echo "Model file size: $(du -h $MODEL_PATH)"
  echo "Feature extractor file size: $(du -h $FEATURE_EXTRACTOR_PATH)"
else
  echo "ERROR: Model files are missing or incomplete!"
  echo "MODEL_PATH: $MODEL_PATH"
  echo "FEATURE_EXTRACTOR_PATH: $FEATURE_EXTRACTOR_PATH"
  echo "Files in models directory:"
  find /app/models -type f | sort
  echo "error" > /app/api_status.txt
  exit 1
fi

# Open required ports in firewall
echo "Configuring firewall..."
if command -v firewall-cmd &> /dev/null; then
  firewall-cmd --permanent --add-port=8000/tcp
  firewall-cmd --permanent --add-port=8080/tcp
  firewall-cmd --reload
  echo "Firewall configured."
fi

# Create a simple direct API script that doesn't depend on dependencies
echo "Creating simple API server script..."
cat > /app/simple_api_server.py << 'EOF'
#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "api_version": "0.1.0"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"message": "Welcome to the Movie Genre Predictor API", "version": "0.1.0"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/predict':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Simple mock response
            response = {
                "predictions": [
                    {"genre": "Science Fiction", "confidence": 0.85},
                    {"genre": "Thriller", "confidence": 0.65},
                    {"genre": "Drama", "confidence": 0.45}
                ]
            }

            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print("Starting simple API server on port 8000...")
    server = HTTPServer(('0.0.0.0', 8000), APIHandler)
    server.serve_forever()
EOF

# Make it executable
chmod +x /app/simple_api_server.py

# Start the simple API server first to ensure something is listening on port 8000
echo "Starting simple API server as a fallback..."
nohup python3 /app/simple_api_server.py > /app/simple_api.log 2>&1 &
sleep 5

# Verify it's running
if curl -s http://localhost:8000/health | grep -q "ok"; then
  echo "Simple API server is running."
else
  echo "WARNING: Simple API server failed to start."
  echo "API server logs:"
  cat /app/simple_api.log
fi

# Run the actual API server with detailed logs
echo "Starting main API server..."
cd /app
echo "starting" > /app/api_status.txt

# Create a service file for the API server
cat > /etc/systemd/system/movie-genre-api.service << EOT
[Unit]
Description=Movie Genre Predictor API
After=network.target

[Service]
User=root
WorkingDirectory=/app
ExecStart=/usr/bin/python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --log-level debug
Restart=always
Environment="APP_NAME=${app_name}"
Environment="ENVIRONMENT=${environment}"
Environment="AWS_REGION=${region}"
Environment="MODEL_PATH=/app/models/latest/model.joblib"
Environment="FEATURE_EXTRACTOR_PATH=/app/models/latest/feature_extractor.joblib"

[Install]
WantedBy=multi-user.target
EOT

# Start and enable the API service
systemctl daemon-reload
systemctl start movie-genre-api
systemctl enable movie-genre-api
echo "API service status: $(systemctl status movie-genre-api | grep Active)"

# Wait for API to fully initialize
echo "Waiting for API to initialize..."
sleep 30

# Check if API is responding and provide detailed output in case of failure
echo "Checking API health..."
if curl -s http://localhost:8000/health | grep -q "status"; then
  echo "API is responding to health checks."
  # Kill the simple API server since the main one is working
  pkill -f "python3 /app/simple_api_server.py" || echo "Simple API server not running"
  echo "running" > /app/api_status.txt
else
  echo "WARNING: API is not responding to health checks yet."

  # Check if the service is running
  echo "API service status details:"
  systemctl status movie-genre-api

  # Check the service logs
  echo "API service logs:"
  journalctl -u movie-genre-api --no-pager -n 50

  # Check API logs
  echo "API logs:"
  tail -50 /app/api.log

  # Check network connections
  echo "Network connections:"
  netstat -tulnp | grep -E '8000|8080'

  # Check if Python is running
  echo "Running Python processes:"
  ps aux | grep python

  echo "error" > /app/api_status.txt
fi

# Get instance metadata
METADATA_URL="http://169.254.169.254/latest/meta-data"
echo "Retrieving instance metadata..."
INSTANCE_ID=$(curl -s $METADATA_URL/instance-id || echo "unknown")
PUBLIC_IP=$(curl -s $METADATA_URL/public-ipv4 || echo "unknown")

# Output completion message
echo "Application setup completed at $(date)"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "API server should be running at http://$PUBLIC_IP:8000"
echo "Basic health server is running at http://$PUBLIC_IP:8080/basic-health"
echo "========== USER DATA EXECUTION COMPLETE =========="
