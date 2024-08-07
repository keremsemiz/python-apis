from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from googletrans import Translator

app = FastAPI()
translator = Translator()

class TranslationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str

@app.post("/translate/", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    try:
        result = translator.translate(request.text, src=request.source_language, dest=request.target_language)
        return TranslationResponse(
            original_text=request.text,
            translated_text=result.text,
            source_language=request.source_language,
            target_language=request.target_language
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))