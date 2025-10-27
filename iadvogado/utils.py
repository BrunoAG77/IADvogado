import io
from datetime import datetime, timedelta
from .config import settings

def make_disclaimer() -> str:
    return (
        "Isto é um resumo gerado automaticamente. Não substitui aconselhamento jurídico. "
        "Para orientação específica, procure a Defensoria Pública ou um advogado."
    )

def expiration_date() -> datetime:
    return datetime.utcnow() + timedelta(days=settings.data_retention_days)