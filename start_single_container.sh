#!/bin/bash

# Iniciar Xvfb em background (para o Chrome funcionar sem tela real)
Xvfb :99 -screen 0 1280x1024x24 &

# Aguardar Xvfb
sleep 1

# Iniciar o servidor Backend (que também serve o Frontend)
echo "🚀 Iniciando VisualFlow Single Container..."
cd /app/backend
uvicorn main:app --host 0.0.0.0 --port 8000
