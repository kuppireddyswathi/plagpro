from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import re
import traceback
import threading
import webbrowser

import nltk

# Safe download of NLTK resources without duplicate errors
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

# Serve frontend from static/
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- ROUTES ----------

@app.route("/")
def home():
    """Serve the frontend homepage."""
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
        return jsonify({
            'filename': filename,
            'extracted_text': extracted_text
        })

    return jsonify({'error': 'Invalid file format'}), 400

def highlight_lines(text, lines):
    for line in sorted(lines, key=len, reverse=True):
        pattern = re.escape(line.strip())
        text = re.sub(pattern, f"<mark>{line.strip()}</mark>", text, flags=re.IGNORECASE)
    return text

@app.route('/check_plagiarism', methods=['POST'])
def check_self_plagiarism():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        result = check_duplicates_in_single_file(text)
        report_text = result.get("report_text", "")
        matched_lines = result.get("matched_lines", [])
        originality_score = result.get("originality_score", 100)

        highlighted_text = highlight_lines(text, matched_lines)

        return jsonify({
            'highlighted_text': highlighted_text,
            'report_text': report_text,
            'originality_score': originality_score,
            'clean_text': text
        })

    except Exception as e:
        print("❌ Error checking duplicates:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/check_citation', methods=['POST'])
def check_citation():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        result = check_citations(text)
        return jsonify({'citation_analysis': result})
    except Exception as e:
        print("❌ Citation Check Error:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/paraphrase', methods=['POST'])
def paraphrase_route():
    data = request.get_json()
    text = data.get('text', '')

    if not text.strip():
        return jsonify({'error': 'No text provided.'}), 400

    try:
        rewritten = paraphrase_paragraphs(text)
        return jsonify({'paraphrased_text': rewritten})
    except Exception as e:
        print("❌ Error during paraphrasing:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

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
            print("✅ PDF Exported to:", output_path)
            return jsonify({'success': True, 'download_url': '/download_pdf'})
        else:
            print("❌ PDF was not created.")
            return jsonify({'error': 'PDF export failed'}), 500
    except Exception as e:
        print("❌ PDF Export Error:", traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'paraphrased_output.pdf')
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "❌ PDF file not found.", 404

@app.route('/health')
def health():
    return jsonify({'status': 'OK'})
import socket
import qrcode
from io import BytesIO
import base64
def get_app_base_url():
    """Return the correct base URL depending on environment."""
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        return f"https://{render_url}"
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"http://{ip}:5000"

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
            h1 {{
                font-size: 28px;
                margin-bottom: 10px;
            }}
            p {{
                font-size: 18px;
            }}
        </style>
    </head>
    <body>
        <h1>📱 Scan to Connect</h1>
        <p>Scan this QR code on your mobile to open ProofWise AI</p>
        <img src="data:image/png;base64,{img_str}" alt="QR Code" />
        <p>Or visit: <b>{url}</b></p>
    </body>
    </html>
    """

@app.route("/get_mobile_qr", methods=["GET"])
def get_mobile_qr():
    session_id = str(uuid.uuid4())
    mobile_url = f"{get_app_base_url()}/mobile-upload/{session_id}"

    # Generate QR
    qr_img = qrcode.make(mobile_url)
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    mobile_sessions[session_id] = None
    return jsonify({"session_id": session_id, "qr_code": img_b64})



# ---------- MAIN ----------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render's PORT or default 5000
    app.run(host="0.0.0.0", port=port, debug=False)

