#!/usr/bin/env python3
"""
Script para testar a configuração do VisualFlow Backend
"""

import sys
import os

def test_imports():
    """Testa se todas as dependências estão instaladas"""
    print("🔍 Testando imports...")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI não encontrado. Execute: pip install fastapi")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError:
        print("❌ Uvicorn não encontrado. Execute: pip install uvicorn")
        return False
    
    try:
        import selenium
        print(f"✅ Selenium: {selenium.__version__}")
    except ImportError:
        print("❌ Selenium não encontrado. Execute: pip install selenium")
        return False
    
    try:
        import pydantic
        print(f"✅ Pydantic: {pydantic.__version__}")
    except ImportError:
        print("❌ Pydantic não encontrado. Execute: pip install pydantic")
        return False
    
    return True

def test_chrome():
    """Testa se o Chrome está disponível"""
    print("\n🌐 Testando Chrome...")
    
    # Caminhos possíveis do Chrome
    chrome_paths = [
        # Windows
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser",
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome encontrado: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        print("⚠️ Chrome não encontrado nos caminhos padrão")
        print("   Instale o Google Chrome ou Chromium")
        print("   Windows: https://www.google.com/chrome/")
        print("   Linux: sudo apt install google-chrome-stable")
        print("   macOS: brew install --cask google-chrome")
    
    return chrome_found

def test_selenium_basic():
    """Testa inicialização básica do Selenium com Service moderno"""
    print("\n🤖 Testando Selenium...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        # Configurar opções
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Tentar inicializar com Selenium Service moderno
        try:
            # Usar Service sem especificar caminho - Selenium gerencia automaticamente
            service = Service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Testar navegação básica
            driver.get("data:text/html,<html><body><h1>Teste Selenium</h1></body></html>")
            title = driver.title
            driver.quit()
            
            print("✅ Selenium funcionando com Service moderno")
            print(f"   Teste de navegação: {title}")
            return True
            
        except Exception as e:
            print(f"⚠️ Selenium Service falhou: {e}")
            
            # Fallback: tentar sem Service explícito
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.get("data:text/html,<html><body><h1>Teste Selenium</h1></body></html>")
                driver.quit()
                print("✅ Selenium funcionando com gerenciamento automático")
                return True
            except Exception as e2:
                print(f"❌ Selenium falhou completamente: {e2}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar Selenium: {e}")
        return False

def test_api_models():
    """Testa se os modelos da API estão funcionando"""
    print("\n📋 Testando modelos da API...")
    
    try:
        from models import FlowData, FlowExecutionStep, NodeType
        print("✅ Modelos importados com sucesso")
        
        # Testar criação de modelo básico
        step = FlowExecutionStep(
            id="test",
            type=NodeType.LOGIN,
            label="Test Step",
            inputs={"url": "https://example.com"},
            position={"x": 0, "y": 0}
        )
        print("✅ Criação de modelo funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos modelos: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Testando configuração do VisualFlow Backend...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Chrome", test_chrome),
        ("Selenium", test_selenium_basic),
        ("Modelos API", test_api_models),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erro no teste {name}: {e}")
            results.append((name, False))
    
    # Resumo
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES:")
    print("="*50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{name:15} {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("🎉 Todos os testes passaram! VisualFlow Backend pronto para uso.")
        print("\nPara iniciar o VisualFlow Backend:")
        print("python start.py")
    else:
        print("⚠️ Alguns testes falharam. Verifique as dependências.")
        print("\nPara instalar dependências:")
        print("pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)