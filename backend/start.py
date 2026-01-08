#!/usr/bin/env python3
"""
Script para iniciar o servidor backend
"""

import uvicorn
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Iniciando VisualFlow Backend...")
    print("📡 API disponível em: http://localhost:8000")
    print("📚 Documentação em: http://localhost:8000/docs")
    print("🔄 Modo de desenvolvimento ativo (auto-reload)")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )