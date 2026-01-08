# 🔧 Guia de Troubleshooting

Soluções para problemas comuns na aplicação de automação visual.

## 🚨 Problemas Comuns

### 1. **Frontend não inicia**

#### Sintomas:
- Erro ao executar `bun run dev`
- Página não carrega em localhost:3001

#### Soluções:
```bash
# Verificar se Bun está instalado
bun --version

# Reinstalar dependências
bun install --force

# Limpar cache
rm -rf node_modules
bun install

# Verificar se porta está livre
netstat -an | findstr :3001  # Windows
lsof -i :3001                # Linux/Mac
```

### 2. **Backend não inicia**

#### Sintomas:
- Erro ao executar `python start.py`
- API não responde em localhost:8000

#### Soluções:
```bash
# Testar configuração
cd backend
python test_setup.py

# Verificar Python
python --version  # Deve ser 3.8+

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall

# Verificar se porta está livre
netstat -an | findstr :8000  # Windows
lsof -i :8000                # Linux/Mac
```

### 3. **Selenium não funciona**

#### Sintomas:
- "Falha ao inicializar o navegador"
- WebDriverException

#### Soluções:

**Windows:**
```bash
# Instalar Chrome
# Baixar de: https://www.google.com/chrome/

# Verificar instalação
dir "C:\Program Files\Google\Chrome\Application\chrome.exe"

# Atualizar webdriver-manager
pip install --upgrade webdriver-manager
```

**Linux:**
```bash
# Instalar Chrome
sudo apt update
sudo apt install google-chrome-stable

# Ou Chromium
sudo apt install chromium-browser

# Verificar instalação
which google-chrome
```

**macOS:**
```bash
# Instalar Chrome
brew install --cask google-chrome

# Verificar instalação
ls "/Applications/Google Chrome.app"
```

### 4. **Erro de CORS**

#### Sintomas:
- Frontend não consegue se comunicar com backend
- Erro "Access-Control-Allow-Origin"

#### Soluções:
```python
# Verificar configuração CORS no backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. **Dependências não encontradas**

#### Sintomas:
- ModuleNotFoundError
- ImportError

#### Soluções:

**Frontend:**
```bash
# Verificar package.json
cat package.json

# Reinstalar
bun install

# Verificar versões
bun list
```

**Backend:**
```bash
# Verificar requirements.txt
cat requirements.txt

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

## 🧪 Scripts de Teste

### 1. **Teste de Configuração Backend**
```bash
cd backend
python test_setup.py
```

### 2. **Teste de Comunicação**
Abra `test-communication.html` no navegador para testar:
- Status do frontend
- Status do backend
- Comunicação CORS
- Execução de fluxo completo

### 3. **Teste Manual da API**
```bash
# Testar health check
curl http://localhost:8000

# Testar listagem de execuções
curl http://localhost:8000/api/executions
```

## 🔍 Logs e Debugging

### Frontend (Browser)
1. Abra DevTools (F12)
2. Vá para Console
3. Procure por erros em vermelho
4. Verifique Network tab para requisições falhadas

### Backend (Terminal)
1. Logs aparecem no terminal onde rodou `python start.py`
2. Procure por linhas com ERROR ou CRITICAL
3. Verifique se todas as dependências foram carregadas

### Selenium (Debugging)
```python
# Adicionar no selenium_executor.py para debug
chrome_options.add_argument("--disable-headless")  # Ver navegador
chrome_options.add_argument("--disable-gpu")       # Evitar problemas gráficos
```

## 🛠️ Soluções Específicas

### **Erro: "Chrome binary not found"**
```bash
# Windows - Verificar caminhos
dir "C:\Program Files\Google\Chrome\Application\chrome.exe"
dir "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

# Adicionar ao PATH ou especificar no código
chrome_options.binary_location = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
```

### **Erro: "Port already in use"**
```bash
# Encontrar processo usando a porta
netstat -ano | findstr :8000  # Windows
lsof -ti:8000                 # Linux/Mac

# Matar processo
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Linux/Mac
```

### **Erro: "Permission denied"**
```bash
# Linux/Mac - Dar permissões
chmod +x backend/start.py
sudo chown -R $USER:$USER .

# Windows - Executar como administrador
```

### **Erro: "Module not found" (Python)**
```bash
# Verificar se está no ambiente virtual correto
which python  # Linux/Mac
where python  # Windows

# Verificar PYTHONPATH
echo $PYTHONPATH  # Linux/Mac
echo %PYTHONPATH% # Windows

# Adicionar diretório atual
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%cd%           # Windows
```

## 📋 Checklist de Verificação

### Antes de Executar:
- [ ] Python 3.8+ instalado
- [ ] Bun instalado
- [ ] Google Chrome instalado
- [ ] Portas 3001 e 8000 livres
- [ ] Dependências instaladas (frontend e backend)

### Durante Execução:
- [ ] Backend rodando em localhost:8000
- [ ] Frontend rodando em localhost:3001
- [ ] API respondendo (teste com curl)
- [ ] CORS configurado corretamente
- [ ] Selenium consegue abrir Chrome

### Teste Final:
- [ ] Consegue criar fluxo no frontend
- [ ] Consegue configurar blocos
- [ ] Consegue executar fluxo remoto
- [ ] Logs aparecem em tempo real
- [ ] Execução completa com sucesso

## 🆘 Suporte Adicional

### Logs Detalhados:
```bash
# Backend com logs verbosos
cd backend
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python start.py

# Frontend com logs de rede
# Abrir DevTools > Network > Preserve log
```

### Informações do Sistema:
```bash
# Versões
python --version
bun --version
google-chrome --version  # Linux/Mac
chrome --version         # Windows

# Sistema operacional
uname -a     # Linux/Mac
systeminfo   # Windows
```

### Contato:
Se os problemas persistirem:
1. Execute `python backend/test_setup.py`
2. Abra `test-communication.html` no navegador
3. Copie todos os logs de erro
4. Inclua informações do sistema (OS, versões)

## 🎯 Dicas de Performance

### Frontend:
- Use `bun run build` para produção
- Desabilite DevTools em produção
- Use cache do navegador

### Backend:
- Configure `headless=True` para Selenium
- Use timeouts apropriados
- Limite execuções simultâneas

### Selenium:
- Desabilite imagens: `--disable-images`
- Desabilite JavaScript: `--disable-javascript`
- Use window size menor: `--window-size=800,600`