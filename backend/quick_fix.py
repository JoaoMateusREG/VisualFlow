#!/usr/bin/env python3
"""
Correção rápida para problemas do ChromeDriver
"""

import os
import sys
import subprocess
import shutil

def log(message):
    print(f"🔧 {message}")

def quick_fix():
    """Correção rápida do ChromeDriver"""
    log("Iniciando correção rápida do ChromeDriver...")
    
    try:
        # 1. Remover ChromeDriver antigo do PATH
        log("Removendo ChromeDriver antigo...")
        
        # Encontrar chromedriver.exe no PATH
        try:
            result = subprocess.run(["where", "chromedriver"], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                paths = result.stdout.strip().split('\n')
                for path in paths:
                    path = path.strip()
                    if path and os.path.exists(path):
                        try:
                            os.remove(path)
                            log(f"✅ Removido: {path}")
                        except PermissionError:
                            log(f"⚠️ Sem permissão para remover: {path}")
                        except Exception as e:
                            log(f"⚠️ Erro ao remover {path}: {e}")
        except:
            log("Nenhum ChromeDriver encontrado no PATH")
        
        # 2. Limpar cache do webdriver-manager
        log("Limpando cache do webdriver-manager...")
        
        cache_paths = [
            os.path.expanduser("~/.wdm"),
            os.path.expanduser("~/AppData/Local/.wdm"),
            os.path.expanduser("~/AppData/Roaming/.wdm"),
        ]
        
        for cache_path in cache_paths:
            if os.path.exists(cache_path):
                try:
                    shutil.rmtree(cache_path)
                    log(f"✅ Cache removido: {cache_path}")
                except Exception as e:
                    log(f"⚠️ Erro ao remover cache {cache_path}: {e}")
        
        # 3. Atualizar webdriver-manager
        log("Atualizando webdriver-manager...")
        
        try:
            # Desinstalar e reinstalar
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "webdriver-manager", "-y"], 
                          capture_output=True)
            
            result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "webdriver-manager"], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                log("✅ webdriver-manager atualizado")
            else:
                log(f"⚠️ Erro ao atualizar webdriver-manager: {result.stderr}")
        
        except Exception as e:
            log(f"⚠️ Erro ao atualizar webdriver-manager: {e}")
        
        # 4. Testar correção
        log("Testando correção...")
        
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get("data:text/html,<html><body><h1>Teste</h1></body></html>")
            driver.quit()
            
            log("✅ Correção bem-sucedida! Selenium funcionando.")
            return True
            
        except Exception as e:
            log(f"⚠️ Teste falhou: {e}")
            log("💡 Usando executor com fallback automático")
            return False
    
    except Exception as e:
        log(f"❌ Erro na correção: {e}")
        return False

if __name__ == "__main__":
    success = quick_fix()
    
    if success:
        log("🎉 ChromeDriver corrigido! Execute: python start.py")
    else:
        log("⚠️ Correção parcial. O sistema usará fallbacks automáticos.")
        log("💡 Execute mesmo assim: python start.py")
    
    input("\nPressione Enter para continuar...")