"""
Version 1.0
This script processes and generates progress reports for a construction project, using data from an Excel file.
"""

from flask import Flask, request, render_template, redirect, url_for, send_file
from pathlib import Path
import zipfile
import shutil
import logging
from datetime import datetime
import socket
from main_script import process_excel_file  # Import the main script function

app = Flask(__name__, static_folder='static')

app.config['UPLOAD_FOLDER'] = Path('uploads')
app.config['PROCESSED_FOLDER'] = Path('processed')
app.config['TEMPLATE_FOLDER'] = Path('template_files')

# Create directories if they do not exist
app.config['UPLOAD_FOLDER'].mkdir(parents=True, exist_ok=True)
app.config['PROCESSED_FOLDER'].mkdir(parents=True, exist_ok=True)
app.config['TEMPLATE_FOLDER'].mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def clean_folder(folder):
    for item in folder.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)

def log_request(filepath, language, prorata_base):
    # Get the user's IP address
    user_ip = request.remote_addr
    # Get the computer name
    computer_name = socket.gethostname()
    # Get the current date and time
    datestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log the information
    logging.info(f"Computer: {computer_name}, IP: {user_ip}, Date: {datestamp}, Filepath: {filepath}, Language: {language}, Prorata Base: {prorata_base}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Clean the upload and processed folders before processing a new file
        clean_folder(app.config['UPLOAD_FOLDER'])
        clean_folder(app.config['PROCESSED_FOLDER'])

        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            filepath = app.config['UPLOAD_FOLDER'] / filename
            file.save(filepath)
            
            language = request.form.get('language')
            prorata_base = request.form.get('prorata_base')
            
            # Log the request
            log_request(filepath, language, prorata_base)
            
            # Process the file with the selected options
            processed_files = process_excel_file(filepath, language, prorata_base)
            
            # Move the processed files to the processed folder
            for processed_file in processed_files:
                shutil.move(str(processed_file), str(app.config['PROCESSED_FOLDER'] / processed_file.name))
            
            # Create a zip file of the processed files
            zip_filename = create_zip_file(app.config['PROCESSED_FOLDER'], filename)
            
            # Redirect to the success page
            return redirect(url_for('success', filename=zip_filename))
    
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(app.config['PROCESSED_FOLDER'] / filename, as_attachment=True)

@app.route('/download_template')
def download_template():
    template_path = app.config['TEMPLATE_FOLDER'] / 'user_template.xlsx'
    return send_file(template_path, as_attachment=True)

@app.route('/success')
def success():
    filename = request.args.get('filename')
    return render_template('success.html', filename=filename)

def create_zip_file(directory, input_filename):
    # Extract the base name of the input file (without extension)
    base_name = Path(input_filename).stem
    # Create the zip file name based on the input file name and today's date in custom format
    current_date = datetime.today().strftime('%Y-%m-%dT%H%M%S')
    zip_filename = f"{base_name}_EA_{current_date}.zip"
    zip_filepath = directory / zip_filename
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.name != zip_filename:
                zipf.write(file_path, arcname=file_path.name)
    return zip_filename

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
