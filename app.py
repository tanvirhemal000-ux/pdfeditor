from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import io
import json
import os
import urllib.request

app = Flask(__name__)

# Montserrat Bold font er direct link
FONT_URL = "https://raw.githubusercontent.com/googlefonts/montserrat/main/fonts/ttf/Montserrat-Bold.ttf"
FONT_PATH = "Montserrat-Bold.ttf"

# Font file ti server e na thakle auto-download korar function
def ensure_font_exists():
    if not os.path.exists(FONT_PATH):
        print("Downloading Montserrat-Bold font...")
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update-pdf', methods=['POST'])
def update_pdf():
    if 'pdf' not in request.files:
        return "No PDF file uploaded", 400
    
    file = request.files['pdf']
    updates_json = request.form.get('updates')
    updates = json.loads(updates_json)

    # Font file ti ready kora
    ensure_font_exists()

    pdf_bytes = file.read()
    doc = fitz.open("pdf", pdf_bytes)

    for page in doc:
        # PDF er vitor Montserrat Bold font ti 'montbold' name e load kora
        page.insert_font(fontname="montbold", fontfile=FONT_PATH)
        
        for old_text, new_text in updates.items():
            if not old_text or not new_text or old_text == new_text:
                continue
            
            instances = page.search_for(old_text)
            for inst in instances:
                # Purano text muche fela (Redaction)
                page.add_redact_annot(inst, "")
                page.apply_redactions()
                
                # Ekdom Apnar Screenshot er Format onujayi Notun Text Bosano
                # Font: Montserrat-Bold, Size: 8
                page.insert_text(
                    fitz.Point(inst.x0, inst.y1 - 1.5), # Alignment thik rakhar jonno ektu upore tola hoyeche
                    new_text, 
                    fontsize=8.0, 
                    fontname="montbold", 
                    color=(0, 0, 0)
                )

    out_pdf = io.BytesIO()
    doc.save(out_pdf)
    doc.close()
    out_pdf.seek(0)

    return send_file(out_pdf, as_attachment=True, download_name="Updated_Receipt.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
