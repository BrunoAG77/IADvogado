#!/usr/bin/env python3
"""
IADvogado - Sistema de IA para simplificação de documentos jurídicos
Ponto de entrada principal da aplicação

Execute este script a partir da raiz do projeto:
    python iadvogado/run.py
Ou use o script da raiz:
    python run_server.py
"""

import sys
import os

# Adicionar o diretório raiz do projeto ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Garantir que o diretório raiz está no path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Mudar para o diretório raiz para garantir imports corretos
os.chdir(parent_dir)

import uvicorn
from iadvogado.api.main import app
from iadvogado.config.config import settings

if __name__ == "__main__":
    print(f"🚀 Iniciando IADvogado em http://{settings.fastapi_host}:{settings.fastapi_port}")
    print(f"📱 Chatbot disponível em http://localhost:{settings.fastapi_port}/")
    print(f"📚 API Docs: http://localhost:{settings.fastapi_port}/docs")
    uvicorn.run(
        app,
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=True
    )


