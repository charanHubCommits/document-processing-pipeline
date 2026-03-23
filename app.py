from flask import Flask, request, render_template
from ocr import extract_text
from extractor import extract_fields
from validator import validate_data
import os
import uuid
import json

app = Flask(__name__)

# Folder to store uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    result = None
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        if file.filename == '':
            return "No file selected"

        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4()) + "_" + file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
            file.save(filepath)

            extracted_text = extract_text(filepath)

            structured_data = extract_fields(extracted_text)

            validation_result = validate_data(structured_data)

            final_output = {
                "data": structured_data,
                "validation": validation_result
            }

            # Save output to file (ACTION)
            output_file = "outputs.json"
            with open(output_file, "a") as f:
                f.write(json.dumps(final_output) + "\n")
            
            result = json.dumps(final_output, indent=4)


            if validation_result["status"] == "VALID":
                with open(output_file, "a") as f:
                    f.write(json.dumps(final_output) + "\n")

            return f"""
            <h3>Extracted Text:</h3>
            <pre>{extracted_text}</pre>

            <h3>Final Output:</h3>
            <pre>{json.dumps(final_output, indent=4)}</pre>
            """

        else:
            return "Invalid file type (Only JPG, JPEG, PNG allowed)"

    return render_template("index.html",result=result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)