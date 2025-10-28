import httpx
from ..config.config import settings

async def send_whatsapp_text(to_number: str, text: str):
    """
    Placeholder adapter. Configure according to the WhatsApp API you choose (Meta, Twilio, 360dialog, etc.).
    Expects WHATSAPP_API_URL and WHATSAPP_API_TOKEN in env.
    """
    if not settings.whatsapp_api_url:
        raise RuntimeError("WHATSAPP_API_URL not configured")

    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "to": to_number,
            "type": "text",
            "text": {"body": text}
        }
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_api_token}",
            "Content-Type": "application/json",
        }
        r = await client.post(settings.whatsapp_api_url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()

async def send_whatsapp_audio(to_number: str, audio_bytes: bytes, filename: str = "explanation.mp3"):
    # Implement according to provider. Many require multipart/form-data upload or a hosted URL for media.
    raise NotImplementedError("Implement provider-specific audio upload")