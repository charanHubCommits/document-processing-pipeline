from flask import Flask, request, render_template, redirect
from ocr import extract_text
from extractor import extract_fields
from validator import validate_data
import os
import uuid
import json

app = Flask(__name__)

LOGS_FOLDER = "logs"
UPLOAD_FOLDER = "uploads"

os.makedirs(LOGS_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    selected_log = None
    selected_filename = None

    if request.method == 'POST':
        file = request.files.get('file')

        if not file or file.filename == '':
            return "No file selected"

        if allowed_file(file.filename):
            filename = str(uuid.uuid4()) + "_" + file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Process
            extracted_text = extract_text(filepath)
            structured_data = extract_fields(extracted_text)
            validation_result = validate_data(structured_data)

            # Confidence
            confidence = 100 - (len(validation_result["errors"]) * 25)
            confidence = max(confidence, 0)

            # Save log
            log_filename = str(uuid.uuid4()) + ".json"
            log_path = os.path.join(LOGS_FOLDER, log_filename)

            log_entry = {
                "filename": filename,
                "raw_text": extracted_text,
                "data": structured_data,
                "validation": validation_result,
                "confidence": confidence
            }

            with open(log_path, "w") as f:
                json.dump(log_entry, f, indent=4)

            selected_log = log_entry
            selected_filename = log_filename

        else:
            return "Invalid file type"

    # Load logs
    logs = sorted(
        [f for f in os.listdir(LOGS_FOLDER) if f.endswith(".json")],
        reverse=True
    )

    return render_template(
        "index.html",
        logs=logs,
        selected_log=selected_log,
        selected_filename=selected_filename
    )


@app.route('/log/<filename>')
def view_log(filename):
    path = os.path.join(LOGS_FOLDER, filename)

    if not os.path.exists(path):
        return "Log not found"

    with open(path, "r") as f:
        log = json.load(f)

    logs = sorted(
        [f for f in os.listdir(LOGS_FOLDER) if f.endswith(".json")],
        reverse=True
    )

    return render_template(
        "index.html",
        logs=logs,
        selected_log=log,
        selected_filename=filename
    )


@app.route('/delete/<filename>')
def delete_log(filename):
    path = os.path.join(LOGS_FOLDER, filename)

    if os.path.exists(path):
        os.remove(path)

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True, port=5001)