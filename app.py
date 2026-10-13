from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import io
import json

app = Flask(__name__)

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

    pdf_bytes = file.read()
    doc = fitz.open("pdf", pdf_bytes)

    for page in doc:
        # PDF er vitor theke exact font properties read korar jonno
        text_dict = page.get_text("dict")
        
        for old_text, new_text in updates.items():
            if not old_text or not new_text or old_text == new_text:
                continue
            
            # Default properties (jodi by chance read korte na pare)
            exact_size = 11.0
            font_name = "helv" # Helvetica Regular
            
            # Original font size ebong Bold/Regular text auto-detect kora
            for block in text_dict.get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if old_text in span.get("text", ""):
                            exact_size = span.get("size", 11.0)
                            # Original lekha bold kiba seta check kora
                            if "bold" in span.get("font", "").lower() or "black" in span.get("font", "").lower():
                                font_name = "hebo" # Helvetica Bold
                            break
            
            # Location khuje ber kora ebong text change kora
            instances = page.search_for(old_text)
            for inst in instances:
                # Purano lekha permanently muche fela
                page.add_redact_annot(inst, "")
                page.apply_redactions()
                
                # Detected Font, Detected Size ebong Exact Location e notun digit bosano
                page.insert_text(
                    fitz.Point(inst.x0, inst.y1 - (exact_size * 0.18)), 
                    new_text, 
                    fontsize=exact_size, 
                    fontname=font_name, 
                    color=(0, 0, 0)
                )

    out_pdf = io.BytesIO()
    doc.save(out_pdf)
    doc.close()
    out_pdf.seek(0)

    return send_file(out_pdf, as_attachment=True, download_name="Updated_Receipt.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
