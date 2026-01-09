#!/usr/bin/env python3
"""
Script para corrigir problemas com Selenium Service e ChromeDriver
Remove ChromeDriver antigo do PATH e força uso do Selenium Manager
"""

import os
import sys
import shutil
from pathlib import Path

def find_chromedriver_in_path():
    """Encontra ChromeDriver no PATH"""
    chromedriver_paths = []
    
    # Verificar PATH
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    
    for path_dir in path_dirs:
        if not path_dir:
            continue
            
        # Possíveis nomes do ChromeDriver
        possible_names = ['chromedriver.exe', 'chromedriver']
        
        for name in possible_names:
            chromedriver_path = Path(path_dir) / name
            if chromedriver_path.exists():
                chromedriver_paths.append(str(chromedriver_path))
    
    return chromedriver_paths

def backup_and_remove_chromedriver(chromedriver_path):
    """Faz backup e remove ChromeDriver antigo"""
    try:
        path = Path(chromedriver_path)
        backup_path = path.with_suffix(path.suffix + '.backup')
        
        print(f"📦 Fazendo backup: {chromedriver_path} -> {backup_path}")
        shutil.move(str(path), str(backup_path))
        
        print(f"✅ ChromeDriver removido: {chromedriver_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao remover {chromedriver_path}: {e}")
        return False

def test_selenium_service():
    """Testa Selenium Service após limpeza"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        print("\n🧪 Testando Selenium Service após limpeza...")
        
        # Configurar opções
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=3")
        
        # Usar Service vazio - força Selenium Manager
        service = Service()
        
        print("🚀 Inicializando Chrome com Selenium Service...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Testar navegação
        driver.get("data:text/html,<html><body><h1>Teste OK</h1></body></html>")
        title = driver.title
        
        # Verificar versões
        chrome_version = driver.capabilities.get('browserVersion', 'N/A')
        driver_version = driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'N/A').split(' ')[0]
        
        driver.quit()
        
        print(f"✅ Selenium Service funcionando!")
        print(f"   Chrome: {chrome_version}")
        print(f"   ChromeDriver: {driver_version}")
        print(f"   Título da página: {title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Selenium Service ainda falhou: {e}")
        return False

def main():
    """Executa correção completa"""
    print("🔧 Corrigindo Selenium Service...\n")
    
    # Encontrar ChromeDrivers no PATH
    chromedriver_paths = find_chromedriver_in_path()
    
    if not chromedriver_paths:
        print("ℹ️ Nenhum ChromeDriver encontrado no PATH")
    else:
        print(f"🔍 Encontrados {len(chromedriver_paths)} ChromeDriver(s) no PATH:")
        for path in chromedriver_paths:
            print(f"   - {path}")
        
        print("\n🗑️ Removendo ChromeDrivers antigos...")
        
        removed_count = 0
        for path in chromedriver_paths:
            if backup_and_remove_chromedriver(path):
                removed_count += 1
        
        print(f"\n📊 Removidos: {removed_count}/{len(chromedriver_paths)} ChromeDrivers")
    
    # Testar Selenium Service
    success = test_selenium_service()
    
    if success:
        print("\n🎉 Selenium Service configurado com sucesso!")
        print("   Agora o Selenium gerencia automaticamente o ChromeDriver")
        print("   Versão compatível será baixada automaticamente")
    else:
        print("\n⚠️ Selenium Service ainda apresenta problemas")
        print("   Possíveis soluções:")
        print("   1. Atualizar Selenium: pip install --upgrade selenium")
        print("   2. Verificar se Chrome está atualizado")
        print("   3. Reiniciar terminal/IDE")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)