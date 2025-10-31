# Minimal storage via Supabase (storing original text, simplified result metadata)
from supabase import create_client
from ..config.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Criar cliente Supabase apenas se configurado
supabase = None
if settings.supabase_url and settings.supabase_key:
    try:
        supabase = create_client(settings.supabase_url, settings.supabase_key)
        logger.info("Supabase cliente inicializado")
    except Exception as e:
        logger.warning(f"Erro ao inicializar Supabase: {e}")
else:
    logger.warning("Supabase não configurado (supabase_url/supabase_key não fornecidos)")

async def save_processing_record(user_id: str | None, raw_text: str, simplified: dict, retention_until: datetime):
    if not supabase:
        logger.debug("Supabase não disponível, pulando salvamento")
        return None
    
    try:
        data = {
            "user_id": user_id,
            "raw_text": raw_text,
            "simplified": simplified,
            "retention_until": retention_until.isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        }
        # Assumes you created a table `processes` with JSON column `simplified` in Supabase
        res = supabase.table('processes').insert(data).execute()
        logger.debug("Registro salvo no Supabase")
        return res
    except Exception as e:
        logger.error(f"Erro ao salvar no Supabase: {e}")
        return None