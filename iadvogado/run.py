#!/usr/bin/env python3
"""
IADvogado - Sistema de IA para simplificação de documentos jurídicos
Ponto de entrada principal da aplicação
"""

import uvicorn
from iadvogado.api.main import app
from iadvogado.config.config import settings

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True
    )
