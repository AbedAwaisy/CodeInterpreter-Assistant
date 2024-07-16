import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from data_assistant.assistant import DataAssistant
from data_assistant.config_manager import ConfigManager
from flask_cors import CORS
import time

app = Flask(__name__)

CORS(app)  # Enable CORS for all routes

class DataAssistantAPI:
    """
    REST API interface for interacting with the Data Assistant.
    """

    def __init__(self):
        self.default_name = "Data Helper"
        self.default_instruction = "You are a helpful assistant; you answer questions based on data and provide charts and graphs to support your answers and insights."
        self.config_manager = ConfigManager()
        self.assistant = None
        self.data_file = None

    def download_data_file(self, url):
        """
        Downloads the data file from the given URL.
        """
        local_filename = 'downloaded_data.csv'
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        self.data_file = local_filename
        return local_filename

    def create_assistant(self, name=None, instruction=None):
        """
        Creates a Data Assistant instance.
        """
        if not self.data_file:
            return "Data file not found. Please upload the data file first."

        if self.config_manager.config_exists():
            return "Configuration exists. Use the existing configuration or delete it to create a new one."

        assistant_name = name or self.default_name
        assistant_instruction = instruction or self.default_instruction
        self.assistant = DataAssistant(self.data_file, assistant_name, assistant_instruction)
        return "Assistant created successfully"

    def follow_up_question(self, question):
        """
        Handles follow-up questions.
        """
        if not self.config_manager.config_exists():
            return "Assistant not created. Please create the assistant first."
        self.assistant = DataAssistant(self.data_file, "", "")
        return self.assistant.follow_up_question(question)

    def reset_configuration(self):
        """
        Resets the configuration by removing the existing config.
        """
        self.config_manager.remove_config()
        self.assistant = None
        self.data_file = None
        return "Configuration reset successfully."


api_interface = DataAssistantAPI()


@app.route('/upload_data', methods=['POST'])
def upload_data():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"message": "URL is required"}), 400
    try:
        filename = api_interface.download_data_file(url)
        return jsonify({"message": f"Data file downloaded successfully: {filename}"}), 201
    except Exception as e:
        return jsonify({"message": f"Failed to download data file: {str(e)}"}), 500


@app.route('/create_assistant', methods=['POST'])
def create_assistant():
    data = request.json
    name = data.get('name')
    instruction = data.get('instruction')
    message = api_interface.create_assistant(name, instruction)
    return jsonify({"message": message}), 201 if "successfully" in message else 200


@app.route('/follow_up', methods=['POST'])
def follow_up():
    data = request.json
    question = data.get('question')
    response = api_interface.follow_up_question(question)
    return jsonify({"response": response}), 200


@app.route('/mock', methods=['POST'])
def mock():
    time.sleep(7)  # Delay for 2 seconds
    file_path = "generated_HTML_report.html"
    return jsonify({"response": file_path}), 200


@app.route('/view_report/<path:filename>', methods=['GET'])
def view_report(filename):
    return send_from_directory(os.getcwd(), filename)  # Serve files from the current working directory


@app.route('/reset_config', methods=['POST'])
def reset_config():
    message = api_interface.reset_configuration()
    return jsonify({"message": message}), 200


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify that the API is running.
    """
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
