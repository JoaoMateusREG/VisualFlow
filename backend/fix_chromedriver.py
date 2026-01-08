#!/usr/bin/env python3
"""
Script para corrigir problemas do ChromeDriver
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def log(message, type="info"):
    icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
    print(f"{icons.get(type, 'ℹ️')} {message}")

def find_chromedriver_in_path():
    """Encontra ChromeDriver no PATH"""
    try:
        result = subprocess.run(["where", "chromedriver"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            paths = result.stdout.strip().split('\n')
            return [path.strip() for path in paths if path.strip()]
    except:
        pass
    return []

def get_chrome_version():
    """Obtém versão do Chrome"""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            try:
                result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split()[-1]
                    return version
            except:
                continue
    return None

def remove_old_chromedriver():
    """Remove ChromeDriver antigo do PATH"""
    log("🔍 Procurando ChromeDriver antigo no PATH...")
    
    drivers = find_chromedriver_in_path()
    if not drivers:
        log("Nenhum ChromeDriver encontrado no PATH")
        return True
    
    for driver_path in drivers:
        try:
            log(f"Removendo ChromeDriver antigo: {driver_path}")
            os.remove(driver_path)
            log(f"✅ Removido: {driver_path}", "success")
        except PermissionError:
            log(f"❌ Sem permissão para remover: {driver_path}", "error")
            log("Execute como administrador ou remova manualmente", "warning")
            return False
        except Exception as e:
            log(f"❌ Erro ao remover {driver_path}: {e}", "error")
            return False
    
    return True

def update_webdriver_manager():
    """Atualiza webdriver-manager"""
    log("📦 Atualizando webdriver-manager...")
    
    try:
        # Desinstalar versão antiga
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "webdriver-manager", "-y"], 
                      capture_output=True)
        
        # Instalar versão mais recente
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "webdriver-manager"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            log("✅ webdriver-manager atualizado com sucesso", "success")
            return True
        else:
            log(f"❌ Erro ao atualizar webdriver-manager: {result.stderr}", "error")
            return False
            
    except Exception as e:
        log(f"❌ Erro ao atualizar webdriver-manager: {e}", "error")
        return False

def test_selenium_fix():
    """Testa se o Selenium está funcionando após correção"""
    log("🧪 Testando Selenium após correção...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Configurar opções
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Tentar inicializar com webdriver-manager
        log("Baixando ChromeDriver compatível...")
        service = Service(ChromeDriverManager().install())
        
        log("Inicializando Chrome WebDriver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Teste básico
        driver.get("data:text/html,<html><body><h1>Teste</h1></body></html>")
        title = driver.title
        driver.quit()
        
        log("✅ Selenium funcionando perfeitamente!", "success")
        return True
        
    except Exception as e:
        log(f"❌ Selenium ainda com problemas: {e}", "error")
        return False

def clear_webdriver_cache():
    """Limpa cache do webdriver-manager"""
    log("🧹 Limpando cache do webdriver-manager...")
    
    try:
        # Caminhos comuns do cache
        cache_paths = [
            os.path.expanduser("~/.wdm"),
            os.path.expanduser("~/AppData/Local/.wdm"),
            os.path.expanduser("~/AppData/Roaming/.wdm"),
        ]
        
        for cache_path in cache_paths:
            if os.path.exists(cache_path):
                shutil.rmtree(cache_path)
                log(f"✅ Cache removido: {cache_path}", "success")
        
        return True
        
    except Exception as e:
        log(f"⚠️ Erro ao limpar cache: {e}", "warning")
        return False

def main():
    """Executa correção completa do ChromeDriver"""
    log("🔧 Iniciando correção do ChromeDriver...")
    
    # Mostrar informações atuais
    chrome_version = get_chrome_version()
    if chrome_version:
        log(f"Chrome detectado: versão {chrome_version}")
    else:
        log("❌ Chrome não encontrado", "error")
        return False
    
    drivers = find_chromedriver_in_path()
    if drivers:
        log(f"ChromeDriver no PATH: {drivers}")
    
    # Passos de correção
    steps = [
        ("Limpando cache do webdriver-manager", clear_webdriver_cache),
        ("Removendo ChromeDriver antigo", remove_old_chromedriver),
        ("Atualizando webdriver-manager", update_webdriver_manager),
        ("Testando correção", test_selenium_fix),
    ]
    
    for step_name, step_func in steps:
        log(f"🔄 {step_name}...")
        if not step_func():
            log(f"❌ Falha em: {step_name}", "error")
            return False
    
    log("🎉 ChromeDriver corrigido com sucesso!", "success")
    log("Agora você pode executar: python start.py")
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        log("\n💡 Soluções alternativas:", "warning")
        log("1. Execute como administrador")
        log("2. Remova manualmente chromedriver.exe do PATH")
        log("3. Reinstale Chrome na versão mais recente")
        log("4. Use modo headless: config.headless = True")
    
    input("\nPressione Enter para continuar...")
    sys.exit(0 if success else 1)