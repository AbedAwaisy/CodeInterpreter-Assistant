#!/bin/bash

# Navigate to the project directory
cd /home/ubuntu/CodeInterpreter-Assistant/data_assistant_project

# Activate virtual environment
source /home/ubuntu/CodeInterpreter-Assistant/venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Export environment variables
export OPENAI_API_KEY=${OPENAI_API_KEY}

# Restart the systemd service
sudo systemctl restart data_assistant.service

echo "Deployment completed successfully."