from flask import Flask, request, render_template, redirect, url_for
from ocr import extract_text
from extractor import extract_fields
from validator import validate_data
import os
import uuid
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["doc_processing"]
collection = db["logs"]

# Folder to store uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    selected_log = None

    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        if file.filename == '':
            return "No file selected"

        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4()) + "_" + file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Process
            extracted_text = extract_text(filepath)
            structured_data = extract_fields(extracted_text)
            validation_result = validate_data(structured_data)

            #STORE IN MONGODB
            log_entry = {
                "filename": filename,
                "raw_text": extracted_text,
                "data": structured_data,
                "validation": validation_result,
            }

            inserted = collection.insert_one(log_entry)
            selected_log = collection.find_one({"_id": inserted.inserted_id})

        else:
            return "Invalid file type"

    #FETCH ALL LOGS
    logs = list(collection.find().sort("_id", -1))

    return render_template(
        "index.html",
        logs=logs,
        selected_log=selected_log
    )
@app.route('/log/<log_id>')
def view_log(log_id):
    log = collection.find_one({"_id": ObjectId(log_id)})
    logs = list(collection.find().sort("_id", -1))

    return render_template(
        "index.html",
        logs=logs,
        selected_log=log
    )


@app.route('/delete/<log_id>')
def delete_log(log_id):
    collection.delete_one({"_id": ObjectId(log_id)})
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)