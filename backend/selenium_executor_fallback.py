from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    StaleElementReferenceException,
    UnexpectedAlertPresentException,
    WebDriverException
)

import time
import asyncio
import os
import sys
import subprocess
from typing import Dict, Any, List, AsyncGenerator
import logging
from datetime import datetime

from models import FlowData, FlowExecutionStep, NodeType, SeleniumConfig

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumExecutorFallback:
    def __init__(self, config: SeleniumConfig = None):
        self.config = config or SeleniumConfig()
        self.driver = None
        self.wait = None
        
    def _get_by_type(self, selector_type: str):
        """Converte string do frontend para tipo By do Selenium"""
        selector_map = {
            'id': By.ID,
            'name': By.NAME,
            'class_name': By.CLASS_NAME,
            'tag_name': By.TAG_NAME,
            'xpath': By.XPATH,
            'css_selector': By.CSS_SELECTOR,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT
        }
        return selector_map.get(selector_type.lower(), By.ID)
    
    def _get_expected_condition(self, condition: str):
        """Converte string do frontend para condição EC do Selenium"""
        condition_map = {
            'presence_of_element_located': EC.presence_of_element_located,
            'visibility_of_element_located': EC.visibility_of_element_located,
            'element_to_be_clickable': EC.element_to_be_clickable,
            'invisibility_of_element_located': EC.invisibility_of_element_located,
            'text_to_be_present_in_element': EC.text_to_be_present_in_element,
            'element_to_be_selected': EC.element_to_be_selected
        }
        return condition_map.get(condition, EC.presence_of_element_located)
    
    def _download_compatible_chromedriver(self):
        """Baixa ChromeDriver compatível manualmente"""
        try:
            logger.info("Tentando baixar ChromeDriver compatível...")
            
            # Obter versão do Chrome
            chrome_version = self._get_chrome_version()
            if not chrome_version:
                return None
            
            # Extrair versão principal (ex: 143 de 143.0.7499.170)
            major_version = chrome_version.split('.')[0]
            
            # URLs de download do ChromeDriver
            import requests
            
            # Tentar API do ChromeDriver
            api_url = f"https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Procurar versão compatível
                for version_info in reversed(data.get('versions', [])):
                    version = version_info.get('version', '')
                    if version.startswith(major_version + '.'):
                        downloads = version_info.get('downloads', {})
                        chromedriver_downloads = downloads.get('chromedriver', [])
                        
                        # Procurar download para Windows
                        for download in chromedriver_downloads:
                            if download.get('platform') == 'win32':
                                download_url = download.get('url')
                                if download_url:
                                    return self._download_and_extract_chromedriver(download_url)
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao baixar ChromeDriver: {e}")
            return None
    
    def _download_and_extract_chromedriver(self, url):
        """Baixa e extrai ChromeDriver"""
        try:
            import requests
            import zipfile
            import tempfile
            
            logger.info(f"Baixando ChromeDriver de: {url}")
            
            # Baixar arquivo
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Salvar em arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_file.write(response.content)
                zip_path = temp_file.name
            
            # Extrair arquivo
            extract_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Procurar chromedriver.exe
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == 'chromedriver.exe':
                        chromedriver_path = os.path.join(root, file)
                        logger.info(f"ChromeDriver extraído em: {chromedriver_path}")
                        return chromedriver_path
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao baixar/extrair ChromeDriver: {e}")
            return None
    
    def _get_chrome_version(self):
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
    
    def _setup_driver(self):
        """Configura e inicializa o driver do Chrome com múltiplos fallbacks"""
        try:
            logger.info("Iniciando configuração do Chrome WebDriver...")
            
            chrome_options = Options()
            
            # Configurações básicas
            if self.config.headless:
                chrome_options.add_argument("--headless")
                logger.info("Modo headless ativado")
            
            chrome_options.add_argument(f"--window-size={self.config.window_size}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--remote-debugging-port=9222")
            
            # Método 1: Tentar webdriver-manager
            try:
                logger.info("Tentativa 1: Usando webdriver-manager...")
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("✅ Sucesso com webdriver-manager")
                
            except Exception as e1:
                logger.warning(f"Webdriver-manager falhou: {e1}")
                
                # Método 2: Tentar ChromeDriver do PATH
                try:
                    logger.info("Tentativa 2: Usando ChromeDriver do PATH...")
                    service = Service()
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("✅ Sucesso com ChromeDriver do PATH")
                    
                except Exception as e2:
                    logger.warning(f"ChromeDriver do PATH falhou: {e2}")
                    
                    # Método 3: Baixar ChromeDriver compatível
                    try:
                        logger.info("Tentativa 3: Baixando ChromeDriver compatível...")
                        chromedriver_path = self._download_compatible_chromedriver()
                        
                        if chromedriver_path and os.path.exists(chromedriver_path):
                            service = Service(chromedriver_path)
                            self.driver = webdriver.Chrome(service=service, options=chrome_options)
                            logger.info("✅ Sucesso com ChromeDriver baixado")
                        else:
                            raise Exception("Não foi possível baixar ChromeDriver compatível")
                            
                    except Exception as e3:
                        logger.error(f"Download do ChromeDriver falhou: {e3}")
                        
                        # Método 4: Usar Selenium Manager (Selenium 4.6+)
                        try:
                            logger.info("Tentativa 4: Usando Selenium Manager...")
                            self.driver = webdriver.Chrome(options=chrome_options)
                            logger.info("✅ Sucesso com Selenium Manager")
                            
                        except Exception as e4:
                            logger.error(f"Selenium Manager falhou: {e4}")
                            raise Exception("Todos os métodos de inicialização falharam")
            
            # Configurar timeouts
            self.driver.implicitly_wait(self.config.implicit_wait)
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            
            self.wait = WebDriverWait(self.driver, self.config.timeout)
            
            logger.info("Driver Chrome inicializado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar driver: {str(e)}")
            return False
    
    def _cleanup_driver(self):
        """Fecha o driver e limpa recursos"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Driver fechado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao fechar driver: {str(e)}")
    
    # Métodos de execução (mesmos do selenium_executor.py original)
    async def execute_step_login(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de navegação/login"""
        try:
            inputs = step.inputs
            logs = []
            
            # Navegar para URL
            url = inputs.get('url', '')
            if url:
                self.driver.get(url)
                self.driver.maximize_window()
                logs.append(f"Navegou para: {url}")
                await asyncio.sleep(1)
            
            # Campo usuário
            username_selector_type = inputs.get('username_selector_type', 'id')
            username_selector = inputs.get('username_selector', '')
            username_value = inputs.get('username_value', '')
            
            if username_selector and username_value:
                by_type = self._get_by_type(username_selector_type)
                timeout = int(inputs.get('wait_time', 10))
                
                username_field = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by_type, username_selector))
                )
                username_field.clear()
                username_field.send_keys(username_value)
                logs.append(f"Preencheu campo usuário: {username_selector}")
            
            # Campo senha
            password_selector_type = inputs.get('password_selector_type', 'id')
            password_selector = inputs.get('password_selector', '')
            password_value = inputs.get('password_value', '')
            
            if password_selector and password_value:
                by_type = self._get_by_type(password_selector_type)
                
                password_field = self.driver.find_element(by_type, password_selector)
                password_field.clear()
                password_field.send_keys(password_value)
                logs.append(f"Preencheu campo senha: {password_selector}")
            
            # Botão login
            login_button_selector_type = inputs.get('login_button_selector_type', 'id')
            login_button_selector = inputs.get('login_button_selector', '')
            
            if login_button_selector:
                by_type = self._get_by_type(login_button_selector_type)
                
                login_button = self.driver.find_element(by_type, login_button_selector)
                login_button.click()
                logs.append(f"Clicou no botão login: {login_button_selector}")
                
                # Pausa após login
                await asyncio.sleep(2)
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            return {"success": False, "error": str(e), "logs": [f"Erro no login: {str(e)}"]}
    
    async def execute_step_click(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de clique em elemento"""
        try:
            inputs = step.inputs
            logs = []
            
            selector_type = inputs.get('selector_type', 'id')
            selector_value = inputs.get('selector_value', '')
            wait_condition = inputs.get('wait_condition', 'element_to_be_clickable')
            wait_timeout = int(inputs.get('wait_timeout', 10))
            
            if not selector_value:
                return {"success": False, "error": "Seletor não informado"}
            
            by_type = self._get_by_type(selector_type)
            condition = self._get_expected_condition(wait_condition)
            
            # Aguardar elemento
            element = WebDriverWait(self.driver, wait_timeout).until(
                condition((by_type, selector_value))
            )
            
            # Scroll se necessário
            if inputs.get('scroll_to_element') == 'true':
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
                logs.append("Rolou até o elemento")
                await asyncio.sleep(0.5)
            
            # Clicar
            if inputs.get('double_click') == 'true':
                ActionChains(self.driver).double_click(element).perform()
                logs.append(f"Duplo clique em: {selector_value}")
            else:
                element.click()
                logs.append(f"Clicou em: {selector_value}")
            
            # Pausa após clique
            pause_after = inputs.get('pause_after', '0')
            if pause_after and float(pause_after) > 0:
                await asyncio.sleep(float(pause_after))
                logs.append(f"Pausou por {pause_after}s")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            return {"success": False, "error": str(e), "logs": [f"Erro no clique: {str(e)}"]}
    
    async def execute_step_input_text(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de inserção de texto"""
        try:
            inputs = step.inputs
            logs = []
            
            selector_type = inputs.get('selector_type', 'id')
            selector_value = inputs.get('selector_value', '')
            text_value = inputs.get('text_value', '')
            wait_condition = inputs.get('wait_condition', 'presence_of_element_located')
            wait_timeout = int(inputs.get('wait_timeout', 10))
            
            if not selector_value:
                return {"success": False, "error": "Seletor não informado"}
            
            by_type = self._get_by_type(selector_type)
            condition = self._get_expected_condition(wait_condition)
            
            # Aguardar elemento
            element = WebDriverWait(self.driver, wait_timeout).until(
                condition((by_type, selector_value))
            )
            
            # Limpar campo se necessário
            if inputs.get('clear_before') == 'true':
                element.clear()
                logs.append("Campo limpo")
            
            # Inserir texto
            element.send_keys(text_value)
            logs.append(f"Inseriu texto '{text_value}' em: {selector_value}")
            
            # Pressionar Enter se necessário
            if inputs.get('press_enter') == 'true':
                element.send_keys(Keys.RETURN)
                logs.append("Pressionou Enter")
            
            # Pausa após inserção
            pause_after = inputs.get('pause_after', '0')
            if pause_after and float(pause_after) > 0:
                await asyncio.sleep(float(pause_after))
                logs.append(f"Pausou por {pause_after}s")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            return {"success": False, "error": str(e), "logs": [f"Erro na inserção: {str(e)}"]}
    
    async def execute_step_wait(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de espera"""
        try:
            inputs = step.inputs
            logs = []
            
            wait_type = inputs.get('wait_type', 'time')
            
            if wait_type == 'time':
                # Espera por tempo fixo
                duration = float(inputs.get('duration', 5))
                await asyncio.sleep(duration)
                logs.append(f"Aguardou {duration}s")
                
            else:
                # Espera por elemento/condição
                selector_type = inputs.get('selector_type', 'id')
                selector_value = inputs.get('selector_value', '')
                wait_condition = inputs.get('wait_condition', 'presence_of_element_located')
                timeout = int(inputs.get('timeout', 30))
                
                if selector_value:
                    by_type = self._get_by_type(selector_type)
                    condition = self._get_expected_condition(wait_condition)
                    
                    # Retry se configurado
                    retry_attempts = int(inputs.get('retry_attempts', 1))
                    
                    for attempt in range(retry_attempts):
                        try:
                            WebDriverWait(self.driver, timeout).until(
                                condition((by_type, selector_value))
                            )
                            logs.append(f"Elemento encontrado: {selector_value}")
                            break
                        except TimeoutException:
                            if attempt < retry_attempts - 1:
                                logs.append(f"Tentativa {attempt + 1} falhou, tentando novamente...")
                                await asyncio.sleep(1)
                            else:
                                raise
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            return {"success": False, "error": str(e), "logs": [f"Erro na espera: {str(e)}"]}
    
    async def execute_flow_async(self, flow_data: FlowData, execution_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Executa o fluxo completo de forma assíncrona"""
        
        # Inicializar driver
        if not self._setup_driver():
            yield {"error": "Falha ao inicializar o navegador Chrome. Verifique se o Chrome está instalado e execute fix_chromedriver.py"}
            return
        
        try:
            total_steps = len(flow_data.executionOrder)
            
            for i, step in enumerate(flow_data.executionOrder):
                yield {
                    "current_step": i + 1,
                    "logs": [f"Executando passo {i + 1}/{total_steps}: {step.label}"]
                }
                
                # Executar passo baseado no tipo
                if step.type == NodeType.LOGIN:
                    result = await self.execute_step_login(step)
                elif step.type == NodeType.CLICK_BUTTON:
                    result = await self.execute_step_click(step)
                elif step.type == NodeType.EXTRACT_TABLE:
                    result = await self.execute_step_input_text(step)
                elif step.type == NodeType.WAIT:
                    result = await self.execute_step_wait(step)
                else:
                    result = {"success": False, "error": f"Tipo de passo não suportado: {step.type}"}
                
                # Enviar resultado do passo
                if result["success"]:
                    yield {
                        "current_step": i + 1,
                        "logs": result.get("logs", []),
                        "results": {f"step_{i+1}": "success"}
                    }
                else:
                    yield {
                        "error": result.get("error", "Erro desconhecido"),
                        "logs": result.get("logs", [])
                    }
                    return
                
                # Pequena pausa entre passos
                await asyncio.sleep(0.5)
            
        finally:
            self._cleanup_driver()
    
    def validate_flow(self, flow_data: FlowData) -> Dict[str, Any]:
        """Valida um fluxo sem executar"""
        errors = []
        warnings = []
        
        if not flow_data.executionOrder:
            errors.append("Fluxo vazio - adicione pelo menos um passo")
        
        for i, step in enumerate(flow_data.executionOrder):
            step_num = i + 1
            
            # Validações específicas por tipo
            if step.type == NodeType.LOGIN:
                if not step.inputs.get('url'):
                    errors.append(f"Passo {step_num}: URL é obrigatória")
                if not step.inputs.get('username_selector'):
                    warnings.append(f"Passo {step_num}: Seletor de usuário não configurado")
                    
            elif step.type == NodeType.CLICK_BUTTON:
                if not step.inputs.get('selector_value'):
                    errors.append(f"Passo {step_num}: Seletor é obrigatório")
                    
            elif step.type == NodeType.EXTRACT_TABLE:
                if not step.inputs.get('selector_value'):
                    errors.append(f"Passo {step_num}: Seletor é obrigatório")
                if not step.inputs.get('text_value'):
                    warnings.append(f"Passo {step_num}: Texto a inserir não configurado")
                    
            elif step.type == NodeType.WAIT:
                wait_type = step.inputs.get('wait_type', 'time')
                if wait_type == 'time' and not step.inputs.get('duration'):
                    errors.append(f"Passo {step_num}: Duração é obrigatória para espera por tempo")
                elif wait_type != 'time' and not step.inputs.get('selector_value'):
                    errors.append(f"Passo {step_num}: Seletor é obrigatório para espera por elemento")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }