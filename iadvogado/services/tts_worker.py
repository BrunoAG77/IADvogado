from gtts import gTTS
import io

def text_to_speech_bytes(text: str, lang: str = 'pt') -> bytes:
    tts = gTTS(text, lang=lang)
    b = io.BytesIO()
    tts.write_to_fp(b)
    b.seek(0)
    return b.read()