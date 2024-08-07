from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fpdf import FPDF
from fastapi.responses import FileResponse
import os

app = FastAPI()

PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

class PDFRequest(BaseModel):
    title: str
    text: str

@app.post("/generate-pdf/")
async def generate_pdf(request: PDFRequest):
    pdf_file = os.path.join(PDF_DIR, f"{request.title}.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, request.text)
    pdf.output(pdf_file)
    return FileResponse(pdf_file)