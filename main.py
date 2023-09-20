import os
import tempfile
import io
from PyPDF2 import PdfReader ,PdfWriter 
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import Flask, request, send_file, render_template

app = Flask(__name__)


def add_watermark(input_pdf_path, output_pdf_path, watermark_text):

    pdf_reader = PdfReader(input_pdf_path)
    pdf_writer = PdfWriter()

    for page in pdf_reader.pages:
        
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        #can.drawString(100, 100, watermark_text)
        x_position = 200 
        y_position = 300  
        #can.setFillColor(0, 0, 0, alpha=0.3)
        can.setFillColor("rgba(0, 0, 0, 0.5)")
        can.setFont("Helvetica", 8)  
      

        start_x = 100
        start_y = 700
        x_increment = 40
        y_increment = -40  

        for i in range(len(watermark_text)):
            x_position = start_x + i * x_increment
            y_position = start_y + i * y_increment
            can.drawString(x_position, y_position, watermark_text)
            
        can.save()
        packet.seek(0)
        watermark = PdfReader(packet)
        page.merge_page(watermark.pages[0]) 

        pdf_writer.add_page(page)
      

    with open(output_pdf_path, 'wb') as output_file:
        pdf_writer.write(output_file)

    return output_pdf_path
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/secure', methods=['POST', 'GET'])
def secure_pdf():
    if request.method == 'POST':
        watermark_text = "CONFIDENTIAL"
        uploaded_file = request.files.get("pdf_file")  

        if not uploaded_file:
            return "No PDF file provided in the request.", 400

        file_extension = os.path.splitext(uploaded_file.filename)[1].lower()
        if file_extension != '.pdf':
            return "Invalid file format. Please upload a PDF file.", 400

        temp_pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_pdf_path = temp_pdf_file.name
        uploaded_file.save(temp_pdf_path)

        output_pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        output_pdf_path = output_pdf_file.name

        secured_pdf_path = add_watermark(temp_pdf_path, output_pdf_path, watermark_text)

        return send_file(secured_pdf_path, as_attachment=True, download_name="secured.pdf")

    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
