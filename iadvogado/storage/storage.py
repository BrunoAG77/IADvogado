# Minimal storage via Supabase (storing original text, simplified result metadata)
from supabase import create_client
from ..config.config import settings
from datetime import datetime

supabase = create_client(settings.supabase_url, settings.supabase_key)

async def save_processing_record(user_id: str | None, raw_text: str, simplified: dict, retention_until: datetime):
    data = {
        "user_id": user_id,
        "raw_text": raw_text,
        "simplified": simplified,
        "retention_until": retention_until.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }
    # Assumes you created a table `processes` with JSON column `simplified` in Supabase
    res = supabase.table('processes').insert(data).execute()
    return res