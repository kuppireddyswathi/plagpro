from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import re
import traceback
import nltk
import qrcode
from io import BytesIO
import base64
import uuid

# Safe NLTK download
for resource in ["punkt", "stopwords", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

from utils import extract_text
from plagiarism_checker import check_duplicates_in_single_file
from citation_checker import check_citations
from paraphraser import paraphrase_paragraphs
from exporter import PDFExporter

# ------------------- App Setup -------------------
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
MOBILE_UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'mobile_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MOBILE_UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

RENDER_URL = "https://plagpro-zaha.onrender.com"
mobile_sessions = {}  # { session_id: filename }


# ------------------- Helpers -------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_app_base_url():
    return RENDER_URL

def highlight_lines(text, lines):
    for line in sorted(lines, key=len, reverse=True):
        pattern = re.escape(line.strip())
        text = re.sub(pattern, f"<mark>{line.strip()}</mark>", text, flags=re.IGNORECASE)
    return text


# ------------------- Main Routes -------------------
@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        extracted_text = extract_text(filepath)
        return jsonify({'filename': filename, 'extracted_text': extracted_text})

    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/check_plagiarism', methods=['POST'])
def check_self_plagiarism():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        result = check_duplicates_in_single_file(text)
        highlighted_text = highlight_lines(text, result.get("matched_lines", []))
        return jsonify({
            'highlighted_text': highlighted_text,
            'report_text': result.get("report_text", ""),
            'originality_score': result.get("originality_score", 100),
            'clean_text': text
        })
    except Exception:
        return jsonify({'error': traceback.format_exc()}), 500

@app.route('/check_citation', methods=['POST'])
def check_citation():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    try:
        return jsonify({'citation_analysis': check_citations(text)})
    except Exception:
        return jsonify({'error': traceback.format_exc()}), 500

@app.route('/paraphrase', methods=['POST'])
def paraphrase_route():
    data = request.get_json()
    text = data.get('text', '')
    if not text.strip():
        return jsonify({'error': 'No text provided.'}), 400
    try:
        return jsonify({'paraphrased_text': paraphrase_paragraphs(text)})
    except Exception:
        return jsonify({'error': traceback.format_exc()}), 500

@app.route('/export_pdf', methods=['POST'])
def export_pdf():
    data = request.get_json()
    paraphrased = data.get('paraphrased_text', '')
    try:
        exporter = PDFExporter()
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'paraphrased_output.pdf')
        exporter.generate_report(paraphrased)
        exporter.export(output_path)
        if os.path.exists(output_path):
            return jsonify({'success': True, 'download_url': '/download_pdf'})
        else:
            return jsonify({'error': 'PDF export failed'}), 500
    except Exception:
        return jsonify({'error': traceback.format_exc()}), 500

@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'paraphrased_output.pdf')
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "❌ PDF file not found.", 404

@app.route('/health')
def health():
    return jsonify({'status': 'OK'})


# ------------------- QR Routes -------------------
@app.route('/generate_qr')
def generate_qr():
    url = get_app_base_url()
    qr_img = qrcode.make(url)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return jsonify({"qr": img_str, "url": url})

@app.route('/qr')
def qr_page():
    url = get_app_base_url()
    qr_img = qrcode.make(url)
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connect with Mobile</title>
        <style>
            body {{
                background: linear-gradient(135deg, #ffffff, #ffcccc);
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
            }}
            img {{
                width: 300px;
                margin-top: 20px;
                border-radius: 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            }}
        </style>
    </head>
    <body>
        <h1>📱 Scan to Connect</h1>
        <p>Scan this QR code to open ProofWise AI</p>
        <img src="data:image/png;base64,{img_str}" />
        <p>Or visit: <b>{url}</b></p>
    </body>
    </html>
    """


# ------------------- Mobile Upload Routes -------------------
@app.route("/get_mobile_qr", methods=["GET"])
def get_mobile_qr():
    session_id = str(uuid.uuid4())
    mobile_url = f"{get_app_base_url()}/mobile-upload/{session_id}"
    qr_img = qrcode.make(mobile_url)
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    mobile_sessions[session_id] = None
    return jsonify({"session_id": session_id, "qr_code": img_b64})
@app.route("/mobile-upload/<session_id>", methods=["GET", "POST"])
def mobile_upload(session_id):
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            filename = f"{session_id}_{file.filename}"
            filepath = os.path.join(MOBILE_UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Immediately extract text just like in /upload
            extracted_text = extract_text(filepath)

            # Store both filename and extracted text
            mobile_sessions[session_id] = {
                "filename": filename,
                "extracted_text": extracted_text
            }
            return "✅ File uploaded & processed. You can close this tab."
        return "❌ No file uploaded."

    # Simple HTML form for mobile
    return """
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial; text-align: center; padding-top: 50px;">
        <h2>Upload to Laptop</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <br><br>
            <button type="submit">Upload</button>
        </form>
    </body>
    </html>
    """

@app.route("/check_mobile_file/<session_id>", methods=["GET"])
def check_mobile_file(session_id):
    session_data = mobile_sessions.get(session_id)
    if session_data:
        return jsonify({
            "ready": True,
            "filename": session_data["filename"],
            "extracted_text": session_data["extracted_text"]
        })
    return jsonify({"ready": False})


# ------------------- Run App -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
