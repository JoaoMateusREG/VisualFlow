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
    # Configurar DATA_DIR para execução local (raiz do projeto/visualflow_data)
    # Isso garante que localmente usemos a mesma estrutura de pastas que o Docker volume
    if not os.getenv("DATA_DIR"):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, "visualflow_data")
        os.makedirs(data_dir, exist_ok=True)
        os.environ["DATA_DIR"] = data_dir
        print(f"📂 Diretório de dados configurado para: {data_dir}")

    print("🚀 Iniciando VisualFlow Backend...")
    print("📡 API disponível em: http://localhost:8164")
    print("📚 Documentação em: http://localhost:8164/docs")
    print("🔄 Modo de desenvolvimento ativo (auto-reload)")
    print("-" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8164,
        reload=True,
        log_level="info"
    )