from flask import Flask, request, send_file, render_template
import fitz  # PyMuPDF
import io
import json
import os
import traceback

app = Flask(__name__)

# Ebar ar kono download hobe na, sorasori github theke file nibe
FONT_PATH = "Montserrat-Bold.ttf"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update-pdf', methods=['POST'])
def update_pdf():
    try:
        if 'pdf' not in request.files:
            return "No PDF file uploaded", 400
        
        file = request.files['pdf']
        updates_json = request.form.get('updates')
        if not updates_json:
            return "No updates data found", 400
            
        updates = json.loads(updates_json)

        pdf_bytes = file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        for page in doc:
            # Local font file ti PDF e embed kora hocche
            if os.path.exists(FONT_PATH):
                page.insert_font(fontname="montbold", fontfile=FONT_PATH)
                font_name_to_use = "montbold"
            else:
                font_name_to_use = "hebo" # Backup font jodi kono karone file na pay
                
            for old_text, new_text in updates.items():
                if not old_text or not new_text or old_text == new_text:
                    continue
                
                if new_text.strip() == "BDT" or new_text.strip() == "":
                    new_text = ""

                instances = page.search_for(old_text)
                for inst in instances:
                    page.add_redact_annot(inst, "")
                    page.apply_redactions()
                    
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
    
    except Exception as e:
        error_details = traceback.format_exc()
        print(error_details)
        return f"Developer Error Code: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
