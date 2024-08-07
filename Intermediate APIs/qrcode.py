from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
import qrcode
import os

app = FastAPI()

QR_DIR = "qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

class QRRequest(BaseModel):
    text: str

@app.post("/qrcode/")
async def generate_qrcode(request: QRRequest):
    qr_file = os.path.join(QR_DIR, f"{request.text}.png")
    img = qrcode.make(request.text)
    img.save(qr_file)
    return FileResponse(qr_file)