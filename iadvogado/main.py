from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from ocr_worker import image_bytes_to_text
from llm_client import simplify_text
from tts_worker import text_to_speech_bytes
from storage import save_processing_record
import asyncio

app = FastAPI(title="IADvogado - Justiça Simples")

@app.post('/upload')
async def upload_document(
    background: BackgroundTasks,
    user_id: str | None = Form(None),
    phone_number: str | None = Form(None),
    file: UploadFile = File(...),
    as_audio: bool = Form(False),
):
    contents = await file.read()
    try:
        raw_text = image_bytes_to_text(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR failed: {e}")

    simplified = await simplify_text(raw_text)
    disclaimer = make_disclaimer()
    payload_text = (
        f"O que aconteceu:\n{simplified['what_happened']}\n\n"
        f"O que significa:\n{simplified['what_it_means']}\n\n"
        f"O que fazer agora:\n{simplified['what_to_do_now']}\n\n"
        f"{disclaimer}"
    )

    # Save record asynchronously
    background.add_task(save_processing_record, user_id, raw_text, simplified, expiration_date())

    # If phone provided, send via WhatsApp (best-effort)
    if phone_number:
        try:
            await send_whatsapp_text(phone_number, payload_text)
        except Exception as e:
            # log and continue
            print('Failed to send WhatsApp message:', e)

        if as_audio:
            try:
                audio_bytes = text_to_speech_bytes(payload_text)
                # provider-specific upload/send needed
                # background.add_task(send_whatsapp_audio, phone_number, audio_bytes)
            except Exception as e:
                print('TTS failed:', e)

    response = {"success": True, "text": payload_text}
    return JSONResponse(response)

@app.post('/process-number')
async def process_by_number(process_number: str = Form(...), user_id: str | None = Form(None), phone_number: str | None = Form(None), as_audio: bool = Form(False)):
    """
    Placeholder: here you would fetch process documents from official court APIs (CNJ, e-SAJ, etc.) if available.
    For MVP we expect the backend to either store a previously-uploaded document or integrate specific court scraping/APIs (requires legal/terms checks).
    """
    # For now return 501 to indicate provider integration needed
    raise HTTPException(status_code=501, detail="Fetch-by-process-number not implemented in MVP. Upload document instead.")

@app.get('/health')
async def health():
    return {"status": "ok"}
