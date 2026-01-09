# VisualFlow - Script de Inicialização
# Este script inicia o backend primeiro, aguarda ele estar pronto, e então inicia o frontend

Write-Host "🚀 Iniciando VisualFlow..." -ForegroundColor Cyan
Write-Host ""

# Verificar se as pastas existem
$backendPath = "$PSScriptRoot\backend"
$frontendPath = $PSScriptRoot

if (-not (Test-Path $backendPath)) {
    Write-Host "❌ Pasta backend não encontrada!" -ForegroundColor Red
    exit 1
}

# Iniciar Backend em uma nova janela
Write-Host "📦 Iniciando Backend..." -ForegroundColor Yellow
$backendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python start.py" -PassThru

# Aguardar o backend ficar pronto
Write-Host "⏳ Aguardando backend ficar pronto..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$backendReady = $false

while ($attempt -lt $maxAttempts -and -not $backendReady) {
    Start-Sleep -Seconds 1
    $attempt++
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
        }
    } catch {
        Write-Host "   Tentativa $attempt/$maxAttempts..." -ForegroundColor Gray
    }
}

if ($backendReady) {
    Write-Host "✅ Backend iniciado com sucesso!" -ForegroundColor Green
    Write-Host ""
    
    # Iniciar Frontend
    Write-Host "🎨 Iniciando Frontend..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; bun run dev"
    
    Write-Host ""
    Write-Host "✅ VisualFlow iniciado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Backend:  http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📍 Frontend: http://localhost:5173" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pressione qualquer tecla para fechar esta janela..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
} else {
    Write-Host "❌ Timeout: Backend não iniciou em tempo!" -ForegroundColor Red
    Write-Host "   Verifique se Python e as dependências estão instaladas." -ForegroundColor Yellow
    exit 1
}
