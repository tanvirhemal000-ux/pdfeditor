from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import io
import json

app = Flask(__name__)

@app.route('/')
def index():
    # Eta apnar HTML frontend ke show korbe
    return render_template('index.html')

@app.route('/update-pdf', methods=['POST'])
def update_pdf():
    if 'pdf' not in request.files:
        return "No PDF file uploaded", 400
    
    file = request.files['pdf']
    updates_json = request.form.get('updates')
    updates = json.loads(updates_json) # Jemon: {"3,360 BDT": "4,000 BDT"}

    pdf_bytes = file.read()
    doc = fitz.open("pdf", pdf_bytes)

    for page in doc:
        for old_text, new_text in updates.items():
            if not old_text or not new_text or old_text == new_text:
                continue
            
            # PyMuPDF diye purano amount search kora
            instances = page.search_for(old_text)
            for inst in instances:
                # Purano text muche fela (Redaction)
                page.add_redact_annot(inst, "")
                page.apply_redactions()
                # Exact same location e notun text bosano
                page.insert_text(fitz.Point(inst.x0, inst.y1 - 1.5), new_text, fontsize=10.5, color=(0, 0, 0))

    out_pdf = io.BytesIO()
    doc.save(out_pdf)
    doc.close()
    out_pdf.seek(0)

    return send_file(out_pdf, as_attachment=True, download_name="Updated_Receipt.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
