from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image, ImageFilter
import os
import shutil
from typing import List

app = FastAPI()

UPLOAD_DIR = "uploaded_images"
PROCESSED_DIR = "processed_images"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@app.post("/process/{filename}")
async def process_image(filename: str, filter: str):
    input_path = os.path.join(UPLOAD_DIR, filename)
    output_path = os.path.join(PROCESSED_DIR, filename)

    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="File not found")

    image = Image.open(input_path)

    if filter == "BLUR":
        image = image.filter(ImageFilter.BLUR)
    elif filter == "CONTOUR":
        image = image.filter(ImageFilter.CONTOUR)
    elif filter == "DETAIL":
        image = image.filter(ImageFilter.DETAIL)
    else:
        raise HTTPException(status_code=400, detail="Invalid filter")

    image.save(output_path)
    return {"filename": filename, "filter": filter}

@app.get("/images/", response_model=List[str])
async def list_images():
    return os.listdir(PROCESSED_DIR)

@app.get("/images/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)