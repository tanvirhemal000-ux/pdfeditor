from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import io
import json
import os
import urllib.request

app = Flask(__name__)

# Ekdom 100% working Montserrat-Bold er ashol link
FONT_URL = "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Bold.ttf"
FONT_PATH = "Montserrat-Bold.ttf"

def ensure_font_exists():
    if not os.path.exists(FONT_PATH):
        try:
            print("Downloading Montserrat-Bold font...")
            # Server theke block na korar jonno User-Agent bebohar kora holo
            req = urllib.request.Request(FONT_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(FONT_PATH, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            print("Font download failed:", e)

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

    # Font download korar chesta kora
    ensure_font_exists()

    pdf_bytes = file.read()
    doc = fitz.open("pdf", pdf_bytes)

    for page in doc:
        # Font properly download hole Montserrat bebohar korbe, noile Helvetica-Bold (hebo)
        font_name_to_use = "hebo"
        if os.path.exists(FONT_PATH):
            page.insert_font(fontname="montbold", fontfile=FONT_PATH)
            font_name_to_use = "montbold"
            
        for old_text, new_text in updates.items():
            if not old_text or not new_text or old_text == new_text:
                continue
            
            # Jodi box faka rakha hoy (jemonta apnar chobite PAID er ghore chilo)
            if new_text.strip() == "BDT" or new_text.strip() == "":
                new_text = ""

            instances = page.search_for(old_text)
            for inst in instances:
                # Purano text muche fela (Redaction)
                page.add_redact_annot(inst, "")
                page.apply_redactions()
                
                # Faka na thaklei shudhumatro notun text print korbe
                if new_text:
                    page.insert_text(
                        fitz.Point(inst.x0, inst.y1 - 1.5), 
                        new_text, 
                        fontsize=8.0, 
                        fontname=font_name_to_use, 
                        color=(0, 0, 0)
                    )

    out_pdf = io.BytesIO()
    doc.save(out_pdf)
    doc.close()
    out_pdf.seek(0)

    return send_file(out_pdf, as_attachment=True, download_name="Updated_Receipt.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
