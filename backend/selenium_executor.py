from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
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
from typing import Dict, Any, List, AsyncGenerator
import logging
from datetime import datetime

from models import FlowData, FlowExecutionStep, NodeType, SeleniumConfig
from pandas_executor import PandasExecutor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumExecutor:
    def __init__(self, config: SeleniumConfig = None):
        self.config = config or SeleniumConfig()
        self.driver = None
        self.wait = None
        self.pandas_executor = PandasExecutor()
        
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
    
    def _setup_driver(self):
        """Configura e inicializa o driver do Chrome usando Selenium Service moderno"""
        try:
            logger.info("🚀 Iniciando Chrome WebDriver com Selenium Service...")
            
            # Configurar opções do Chrome
            chrome_options = Options()
            
            # Configurações básicas de performance e estabilidade
            if self.config.headless:
                chrome_options.add_argument("--headless=new")  # Novo modo headless
                logger.info("🔇 Modo headless ativado")
            
            # Configurações de janela e performance
            chrome_options.add_argument(f"--window-size={self.config.window_size}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            
            # Configurações de rede e cache
            chrome_options.add_argument("--aggressive-cache-discard")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-sync")
            
            # Configurações de segurança e privacidade
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-log-file")
            chrome_options.add_argument("--log-level=3")  # Apenas erros críticos
            
            # Configurações experimentais para melhor compatibilidade
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Prefs para desabilitar notificações e popups
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,  # Bloquear notificações
                    "popups": 2,         # Bloquear popups
                },
                "profile.managed_default_content_settings": {
                    "images": 2 if self.config.headless else 1  # Bloquear imagens apenas em headless
                },
                "download.default_directory": os.getenv("DATA_DIR", "/app/data"),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Usar Selenium Service moderno (Selenium 4.6+)
            logger.info("🔧 Usando Selenium Service com gerenciamento automático de driver...")
            
            # Criar Service sem especificar caminho - Selenium gerencia automaticamente
            service = Service()
            
            # Inicializar driver com Service moderno
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configurar timeouts
            self.driver.implicitly_wait(self.config.implicit_wait)
            self.driver.set_page_load_timeout(self.config.page_load_timeout)
            
            # Configurar WebDriverWait
            self.wait = WebDriverWait(self.driver, self.config.timeout)
            
            # Executar script para remover indicadores de automação
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("✅ Chrome WebDriver inicializado com sucesso via Selenium Service")
            
            # Log da versão do Chrome e ChromeDriver
            try:
                chrome_version = self.driver.capabilities['browserVersion']
                driver_version = self.driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]
                logger.info(f"🌐 Chrome: {chrome_version}")
                logger.info(f"🔧 ChromeDriver: {driver_version}")
            except:
                logger.info("ℹ️ Versões do Chrome/ChromeDriver não disponíveis")
            
            return True
            
        except WebDriverException as e:
            logger.error(f"❌ Erro do WebDriver: {str(e)}")
            logger.error("💡 Dica: Verifique se o Chrome está instalado e atualizado")
            return False
        except Exception as e:
            logger.error(f"❌ Erro geral ao inicializar driver: {str(e)}")
            return False
    
    def _cleanup_driver(self):
        """Fecha o driver e limpa recursos"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None # Marcar como fechado
                logger.info("✅ Driver fechado com sucesso")
            except Exception as e:
                logger.error(f"⚠️ Erro ao fechar driver: {str(e)}")

    async def execute_step_close_browser(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de fechar navegador"""
        try:
            self._cleanup_driver()
            return {"success": True, "logs": ["Navegador fechado com sucesso"]}
        except Exception as e:
            return {"success": False, "error": str(e), "logs": [f"Erro ao fechar navegador: {str(e)}"]}
    
    async def execute_step_login(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de navegação/login"""
        try:
            inputs = self.substitute_variables_in_inputs(step.inputs)
            logs = []
            
            # Navegar para URL
            url = inputs.get('url', '')
            if url:
                logger.info(f"🌐 Navegando para: {url}")
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
                
                logger.info(f"👤 Preenchendo campo usuário: {username_selector}")
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
                
                logger.info(f"🔒 Preenchendo campo senha: {password_selector}")
                password_field = self.driver.find_element(by_type, password_selector)
                password_field.clear()
                password_field.send_keys(password_value)
                logs.append(f"Preencheu campo senha: {password_selector}")
            
            # Botão login
            login_button_selector_type = inputs.get('login_button_selector_type', 'id')
            login_button_selector = inputs.get('login_button_selector', '')
            
            if login_button_selector:
                by_type = self._get_by_type(login_button_selector_type)
                
                logger.info(f"🔘 Clicando no botão login: {login_button_selector}")
                login_button = self.driver.find_element(by_type, login_button_selector)
                login_button.click()
                logs.append(f"Clicou no botão login: {login_button_selector}")
                
                # Pausa após login
                await asyncio.sleep(2)
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro no login: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro no login: {str(e)}"]}
    
    async def execute_step_open_site(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de acessar site (apenas navegação)"""
        try:
            inputs = self.substitute_variables_in_inputs(step.inputs)
            logs = []
            
            # Navegar para URL
            url = inputs.get('url', '')
            if not url:
                return {"success": False, "error": "URL não informada", "logs": ["Erro: URL não informada"]}
            
            logger.info(f"🌐 Navegando para: {url}")
            self.driver.get(url)
            self.driver.maximize_window()
            logs.append(f"Navegou para: {url}")
            
            # Aguardar tempo especificado
            wait_time = float(inputs.get('wait_time', 0))
            if wait_time > 0:
                logger.info(f"⏳ Aguardando {wait_time} segundos...")
                await asyncio.sleep(wait_time)
                logs.append(f"Aguardou {wait_time} segundos")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro ao acessar site: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro ao acessar site: {str(e)}"]}
    
    async def execute_step_capture_table(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de captura de tabela HTML"""
        try:
            inputs = self.substitute_variables_in_inputs(step.inputs)
            logs = []
            
            selector_type = inputs.get('selector_type', 'xpath')
            selector_value = inputs.get('selector_value', '')
            variable_name = inputs.get('variable_name', 'df_table')
            include_headers = inputs.get('include_headers', 'false') == 'true'
            wait_condition = inputs.get('wait_condition', 'presence_of_element_located')
            wait_timeout = int(inputs.get('wait_timeout', 10))
            skip_empty_rows = inputs.get('skip_empty_rows', 'false') == 'true'
            
            if not selector_value:
                return {"success": False, "error": "Seletor da tabela não informado"}
            
            by_type = self._get_by_type(selector_type)
            condition = self._get_expected_condition(wait_condition)
            
            logger.info(f"📊 Aguardando tabela: {selector_value}")
            
            # Aguardar tabela estar presente
            table_element = WebDriverWait(self.driver, wait_timeout).until(
                condition((by_type, selector_value))
            )
            
            # Encontrar todas as linhas (tr) dentro da tabela
            rows = table_element.find_elements(By.TAG_NAME, 'tr')
            logs.append(f"Tabela encontrada com {len(rows)} linhas")
            
            # Lista para armazenar dados
            table_data = []
            
            # Processar cada linha
            for row_index, row in enumerate(rows):
                # Encontrar todas as células (td ou th) na linha
                cells = row.find_elements(By.TAG_NAME, 'td')
                if not cells:
                    # Se não houver td, tentar th (cabeçalho)
                    cells = row.find_elements(By.TAG_NAME, 'th')
                
                # Extrair texto de cada célula
                row_data = [cell.text.strip() for cell in cells]
                
                # Pular linhas vazias se solicitado
                if skip_empty_rows and not any(row_data):
                    continue
                
                # Se for a primeira linha e include_headers for True, usar como cabeçalho
                if row_index == 0 and include_headers and cells:
                    # Verificar se são células de cabeçalho (th)
                    if cells[0].tag_name.lower() == 'th':
                        # Esta linha será o cabeçalho do DataFrame
                        table_data.append(row_data)
                    else:
                        # Adicionar linha normal
                        table_data.append(row_data)
                else:
                    # Adicionar linha normal
                    table_data.append(row_data)
            
            # Criar DataFrame usando pandas_executor
            import pandas as pd
            df = pd.DataFrame(table_data)
            
            # Se include_headers e houver dados, usar primeira linha como cabeçalho
            if include_headers and len(df) > 0:
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
            
            # Armazenar DataFrame no pandas_executor
            self.pandas_executor.dataframes[variable_name] = df
            self.pandas_executor.variables[variable_name] = df
            
            logs.append(f"Tabela capturada e armazenada em: {variable_name}")
            logs.append(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            
            if len(df) > 0:
                logs.append(f"Colunas: {', '.join(df.columns.astype(str).tolist())}")
            
            logger.info(f"✅ Tabela capturada: {df.shape[0]} linhas, {df.shape[1]} colunas")
            
            return {"success": True, "logs": logs, "rows_captured": len(df), "columns": df.shape[1]}
            
        except Exception as e:
            logger.error(f"❌ Erro ao capturar tabela: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro ao capturar tabela: {str(e)}"]}
    
    async def execute_step_click(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de clique em elemento"""
        try:
            inputs = self.substitute_variables_in_inputs(step.inputs)
            logs = []
            
            selector_type = inputs.get('selector_type', 'id')
            selector_value = inputs.get('selector_value', '')
            wait_condition = inputs.get('wait_condition', 'element_to_be_clickable')
            wait_timeout = int(inputs.get('wait_timeout', 10))
            
            if not selector_value:
                return {"success": False, "error": "Seletor não informado"}
            
            by_type = self._get_by_type(selector_type)
            condition = self._get_expected_condition(wait_condition)
            
            logger.info(f"🖱️ Aguardando elemento clicável: {selector_value}")
            
            # Aguardar elemento
            element = WebDriverWait(self.driver, wait_timeout).until(
                condition((by_type, selector_value))
            )
            
            # Scroll se necessário
            if inputs.get('scroll_to_element') == 'true':
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                logs.append("Rolou até o elemento")
                await asyncio.sleep(0.5)
            
            # Verificar se é seleção de opção em select
            option_index = inputs.get('option_index')
            if option_index is not None:
                # É um select, selecionar opção pelo índice
                try:
                    # Substituir variável se necessário
                    if isinstance(option_index, str) and option_index.startswith('${'):
                        var_name = option_index[2:-1]
                        option_index = self.pandas_executor.get_variable_value(var_name, 0)
                    
                    option_index = int(option_index)
                    options = element.find_elements(By.TAG_NAME, 'option')
                    if option_index < len(options):
                        options[option_index].click()
                        logs.append(f"Selecionou opção {option_index} do select (total: {len(options)})")
                        logger.info(f"✅ Selecionou opção {option_index} do select")
                    else:
                        return {"success": False, "error": f"Índice de opção inválido: {option_index} (total: {len(options)})"}
                except Exception as e:
                    return {"success": False, "error": f"Erro ao selecionar opção: {str(e)}"}
            else:
                # Clicar normalmente
                if inputs.get('double_click') == 'true':
                    ActionChains(self.driver).double_click(element).perform()
                    logs.append(f"Duplo clique em: {selector_value}")
                    logger.info(f"🖱️ Duplo clique executado em: {selector_value}")
                else:
                    element.click()
                    logs.append(f"Clicou em: {selector_value}")
                    logger.info(f"🖱️ Clique executado em: {selector_value}")
            
            # Pausa após clique
            pause_after = inputs.get('pause_after', '0')
            if pause_after and float(pause_after) > 0:
                await asyncio.sleep(float(pause_after))
                logs.append(f"Pausou por {pause_after}s")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro no clique: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro no clique: {str(e)}"]}
    
    async def execute_step_input_text(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de inserção de texto"""
        try:
            inputs = self.substitute_variables_in_inputs(step.inputs)
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
            
            logger.info(f"⌨️ Aguardando campo de texto: {selector_value}")
            
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
            logger.info(f"⌨️ Texto inserido em {selector_value}: {text_value}")
            
            # Pressionar Enter se necessário
            if inputs.get('press_enter') == 'true':
                element.send_keys(Keys.RETURN)
                logs.append("Pressionou Enter")
                logger.info("⏎ Enter pressionado")
            
            # Pausa após inserção
            pause_after = inputs.get('pause_after', '0')
            if pause_after and float(pause_after) > 0:
                await asyncio.sleep(float(pause_after))
                logs.append(f"Pausou por {pause_after}s")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro na inserção: {str(e)}")
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
                logger.info(f"⏱️ Aguardando {duration}s...")
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
                    
                    logger.info(f"⏳ Aguardando elemento: {selector_value}")
                    
                    # Retry se configurado
                    retry_attempts = int(inputs.get('retry_attempts', 1))
                    
                    for attempt in range(retry_attempts):
                        try:
                            WebDriverWait(self.driver, timeout).until(
                                condition((by_type, selector_value))
                            )
                            logs.append(f"Elemento encontrado: {selector_value}")
                            logger.info(f"✅ Elemento encontrado: {selector_value}")
                            break
                        except TimeoutException:
                            if attempt < retry_attempts - 1:
                                logs.append(f"Tentativa {attempt + 1} falhou, tentando novamente...")
                                logger.warning(f"⚠️ Tentativa {attempt + 1} falhou, tentando novamente...")
                                await asyncio.sleep(1)
                            else:
                                raise
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro na espera: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro na espera: {str(e)}"]}
    
    async def execute_step_sleep(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de pausa (sleep)"""
        try:
            inputs = step.inputs
            logs = []
            
            # Obter duração da pausa
            duration = float(inputs.get('duration', 2))
            description = inputs.get('description', '')
            
            if description:
                logger.info(f"😴 Pausando por {duration}s - {description}")
                logs.append(f"Pausando por {duration}s - {description}")
            else:
                logger.info(f"😴 Pausando por {duration}s...")
                logs.append(f"Pausando por {duration}s")
            
            # Executar pausa
            await asyncio.sleep(duration)
            
            logger.info(f"✅ Pausa de {duration}s concluída")
            logs.append(f"Pausa concluída")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro na pausa: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro na pausa: {str(e)}"]}
    
    async def execute_step_spreadsheet(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de planilha"""
        return await self.pandas_executor.execute_step_spreadsheet(step)
    
    async def execute_step_variable(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de variável"""
        return await self.pandas_executor.execute_step_variable(step)
    
    async def execute_step_loop_for(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de loop for"""
        return await self.pandas_executor.execute_step_loop_for(step)
    
    async def execute_step_schedule(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de agendamento"""
        try:
            inputs = step.inputs
            logs = []
            
            schedule_type = inputs.get('schedule_type', 'daily')
            time_str = inputs.get('time', '09:00')
            timezone = inputs.get('timezone', 'America/Sao_Paulo')
            
            logger.info(f"⏰ Configurando agendamento: {schedule_type}")
            
            # Validar formato do horário
            try:
                hour, minute = map(int, time_str.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError("Horário inválido")
            except ValueError:
                return {"success": False, "error": f"Formato de horário inválido: {time_str}. Use HH:MM"}
            
            # Processar diferentes tipos de agendamento
            schedule_info = {
                "type": schedule_type,
                "time": time_str,
                "timezone": timezone
            }
            
            if schedule_type == 'daily':
                logs.append(f"Agendamento diário configurado para {time_str}")
                schedule_info["description"] = f"Execução diária às {time_str}"
                
            elif schedule_type == 'weekly':
                days_of_week = inputs.get('days_of_week', 'monday').split(',')
                schedule_info["days_of_week"] = [day.strip() for day in days_of_week]
                days_pt = {
                    'monday': 'Segunda', 'tuesday': 'Terça', 'wednesday': 'Quarta',
                    'thursday': 'Quinta', 'friday': 'Sexta', 'saturday': 'Sábado', 'sunday': 'Domingo'
                }
                days_display = ', '.join([days_pt.get(day, day) for day in schedule_info["days_of_week"]])
                logs.append(f"Agendamento semanal configurado para {days_display} às {time_str}")
                schedule_info["description"] = f"Execução semanal ({days_display}) às {time_str}"
                
            elif schedule_type == 'monthly':
                days_of_month = inputs.get('days_of_month', '1')
                schedule_info["days_of_month"] = [int(day.strip()) for day in days_of_month.split(',')]
                logs.append(f"Agendamento mensal configurado para os dias {days_of_month} às {time_str}")
                schedule_info["description"] = f"Execução mensal (dias {days_of_month}) às {time_str}"
                
            elif schedule_type == 'interval':
                interval_minutes = int(inputs.get('interval_minutes', 60))
                schedule_info["interval_minutes"] = interval_minutes
                logs.append(f"Agendamento por intervalo configurado para a cada {interval_minutes} minutos")
                schedule_info["description"] = f"Execução a cada {interval_minutes} minutos"
                
            elif schedule_type == 'cron':
                cron_expression = inputs.get('cron_expression', '0 9 * * *')
                schedule_info["cron_expression"] = cron_expression
                logs.append(f"Agendamento cron configurado: {cron_expression}")
                schedule_info["description"] = f"Execução cron: {cron_expression}"
            
            # Configurações opcionais
            if inputs.get('start_date'):
                schedule_info["start_date"] = inputs.get('start_date')
                logs.append(f"Data de início: {inputs.get('start_date')}")
                
            if inputs.get('end_date'):
                schedule_info["end_date"] = inputs.get('end_date')
                logs.append(f"Data de fim: {inputs.get('end_date')}")
                
            if inputs.get('max_executions'):
                schedule_info["max_executions"] = int(inputs.get('max_executions'))
                logs.append(f"Máximo de execuções: {inputs.get('max_executions')}")
            
            # Salvar configuração de agendamento (em produção, isso seria salvo em banco de dados)
            logger.info(f"✅ Agendamento configurado: {schedule_info['description']}")
            logs.append("Agendamento salvo com sucesso")
            
            # Nota: Em uma implementação completa, aqui seria integrado com um scheduler
            # como Celery, APScheduler ou similar para executar o workflow nos horários definidos
            logs.append("⚠️ Nota: Para ativar o agendamento, integre com um sistema de scheduler")
            
            return {
                "success": True, 
                "logs": logs,
                "schedule_config": schedule_info
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no agendamento: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro no agendamento: {str(e)}"]}
    
    async def execute_step_execute_script(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa JavaScript customizado na página"""
        try:
            inputs = self.substitute_variables_in_inputs(step.inputs)
            logs = []
            
            script = inputs.get('script', '')
            variable_name = inputs.get('variable_name', '') # Opcional, para salvar retorno
            
            if not script:
                return {"success": False, "error": "Script não informado"}
                
            logger.info("📜 Executando JavaScript customizado...")
            
            # Executar script
            result = self.driver.execute_script(script)
            
            logs.append("Script executado com sucesso")
            
            if variable_name:
                self.pandas_executor.variables[variable_name] = result
                logs.append(f"Retorno salvo na variável: {variable_name} = {result}")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro na execução de script: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro na execução de script: {str(e)}"]}

    async def execute_step_extract_text(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Extrai texto de elemento usando Regex"""
        try:
            inputs = self.substitute_variables_in_inputs(step.inputs)
            logs = []
            
            selector_type = inputs.get('selector_type', 'xpath')
            selector_value = inputs.get('selector_value', '')
            regex_pattern = inputs.get('regex_pattern', '')
            variable_name = inputs.get('variable_name', 'extracted_text')
            wait_timeout = int(inputs.get('wait_timeout', 10))
            
            # Se true, procura em todo outerHTML/text do body se falhar o seletor
            fallback_to_body = inputs.get('fallback_to_body', 'false') == 'true' 
            fallback_regex_pattern = inputs.get('fallback_regex_pattern', '')
            
            extracted_value = None
            
            # Tentar extrair do elemento específico
            if selector_value:
                try:
                    by_type = self._get_by_type(selector_type)
                    element = WebDriverWait(self.driver, wait_timeout).until(
                        EC.presence_of_element_located((by_type, selector_value))
                    )
                    text_content = element.text
                    logs.append(f"Texto obtido do elemento: {text_content[:50]}...")
                    
                    if regex_pattern:
                        import re
                        match = re.search(regex_pattern, text_content)
                        if match:
                            # Se tiver grupos, pega o primeiro grupo, senão pega tudo
                            if match.groups():
                                extracted_value = match.group(1)
                            else:
                                extracted_value = match.group(0)
                            logs.append(f"Regex match: {extracted_value}")
                        else:
                            logs.append("Regex não encontrou correspondência no elemento.")
                    else:
                        extracted_value = text_content
                        
                except Exception as e:
                    logs.append(f"Erro ao extrair do seletor: {str(e)}")
            
            # Fallback para o body se necessário
            if extracted_value is None and fallback_to_body:
                logger.info("⚠️ Tentando fallback no body...")
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, 'body').text
                    import re
                    pattern_to_use = fallback_regex_pattern if fallback_regex_pattern else regex_pattern
                    match = re.search(pattern_to_use, body_text, re.IGNORECASE)
                    if match:
                         if match.groups():
                            extracted_value = match.group(1)
                         else:
                            extracted_value = match.group(0)
                         logs.append(f"Regex match no BODY: {extracted_value}")
                    else:
                        logs.append("Regex não encontrou correspondência no BODY.")
                except Exception as e:
                    logs.append(f"Erro no fallback do body: {str(e)}")

            if extracted_value is not None:
                self.pandas_executor.variables[variable_name] = extracted_value
                logs.append(f"Valor extraído salvo em '{variable_name}': {extracted_value}")
                return {"success": True, "logs": logs}
            else:
                return {"success": False, "error": "Não foi possível extrair o texto desejado", "logs": logs}

        except Exception as e:
            logger.error(f"❌ Erro na extração de texto: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro na extração de texto: {str(e)}"]}

    async def execute_step_condition(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de condição"""
        return await self.pandas_executor.execute_step_condition(step)
    
    async def execute_step_loop_while(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de loop while"""
        return await self.pandas_executor.execute_step_loop_while(step)

    async def execute_step_python(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa código Python arbitrário (generic/white-label)"""
        try:
            inputs = step.inputs
            # Não fazemos substituição automática de variáveis aqui para não quebrar sintaxe python
            # O usuário acessa variáveis via dicionário 'variables'
            
            code = inputs.get('code', '')
            
            if not code:
                return {"success": False, "error": "Código Python não informado"}
                
            logger.info("🐍 Executando código Python customizado...")
            
            # Preparar contexto
            context = {
                'driver': self.driver,
                'variables': self.pandas_executor.variables,
                'dataframes': self.pandas_executor.dataframes,
                'pd': __import__('pandas'),
                'time': __import__('time'),
                're': __import__('re'),
                'WebDriverWait': WebDriverWait,
                'By': By,
                'EC': EC,
                'logger': logger,
                'print': print
            }
            
            # Capturar stdout
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            
            # Executar código
            with redirect_stdout(f):
                exec(code, context)
            
            output = f.getvalue()
            logs = [line for line in output.split('\n') if line]
            logs.append("Código Python executado com sucesso")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro na execução de Python: {str(e)}")
            import traceback
            trace_str = traceback.format_exc()
            return {"success": False, "error": str(e), "logs": [f"Erro Python: {str(e)}", trace_str]}
    
    def substitute_variables_in_inputs(self, inputs: Dict[str, str]) -> Dict[str, str]:
        """Substitui variáveis nos inputs usando o pandas_executor"""
        substituted = {}
        for key, value in inputs.items():
            if isinstance(value, str):
                substituted[key] = self.pandas_executor.substitute_variables(value)
            else:
                substituted[key] = value
        return substituted
    
    def _find_loop_body(self, loop_step_id: str, execution_order: List[FlowExecutionStep], edges: List[Dict]) -> List[int]:
        """Encontra os índices dos passos que estão dentro do loop"""
        # Criar mapa de edges (source -> [targets])
        edge_map = {}
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            if source not in edge_map:
                edge_map[source] = []
            edge_map[source].append(target)
        
        # Criar mapa reverso (target -> [sources])
        reverse_edge_map = {}
        for edge in edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            if target not in reverse_edge_map:
                reverse_edge_map[target] = []
            reverse_edge_map[target].append(source)
        
        # Encontrar índice do loop
        loop_index = None
        for i, step in enumerate(execution_order):
            if step.id == loop_step_id:
                loop_index = i
                break
        
        if loop_index is None:
            return []
        
        # Encontrar todos os passos que são alcançáveis a partir do loop
        # usando BFS a partir do loop
        loop_body_indices = []
        visited = set()
        queue = [loop_step_id]
        
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # Encontrar índice do passo atual
            current_index = None
            for idx, step in enumerate(execution_order):
                if step.id == current_id:
                    current_index = idx
                    break
            
            # Se o passo está depois do loop na ordem de execução, adicionar ao corpo do loop
            if current_index is not None and current_index > loop_index:
                # Verificar se este passo não é alcançável diretamente a partir de passos antes do loop
                # (exceto através do loop)
                is_directly_connected_to_pre_loop = False
                if current_id in reverse_edge_map:
                    for source in reverse_edge_map[current_id]:
                        # Encontrar índice da source
                        source_index = None
                        for idx, step in enumerate(execution_order):
                            if step.id == source:
                                source_index = idx
                                break
                        # Se a source está antes do loop, este passo não está no loop
                        if source_index is not None and source_index < loop_index:
                            is_directly_connected_to_pre_loop = True
                            break
                
                if not is_directly_connected_to_pre_loop and current_index not in loop_body_indices:
                    loop_body_indices.append(current_index)
            
            # Adicionar próximos passos à fila
            if current_id in edge_map:
                for next_id in edge_map[current_id]:
                    if next_id not in visited:
                        queue.append(next_id)
        
        return sorted(loop_body_indices)
    
    def _is_reachable(self, start_id: str, target_id: str, edge_map: Dict) -> bool:
        """Verifica se target_id é alcançável a partir de start_id"""
        if start_id == target_id:
            return True
        
        visited = set()
        queue = [start_id]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            if current == target_id:
                return True
            
            if current in edge_map:
                for next_node in edge_map[current]:
                    if next_node not in visited:
                        queue.append(next_node)
        
        return False
    
    async def execute_flow_async(self, flow_data: FlowData, execution_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Executa o fluxo completo de forma assíncrona"""
        
        logger.info(f"🚀 Iniciando execução do fluxo: {flow_data.metadata.name}")
        
        # Inicializar driver
        if not self._setup_driver():
            yield {"error": "Falha ao inicializar o navegador Chrome. Verifique se o Chrome está instalado e atualizado."}
            return
        
        try:
            execution_order = flow_data.executionOrder
            edges = flow_data.rawData.get('edges', [])
            total_steps = len(execution_order)
            logger.info(f"📋 Total de passos: {total_steps}")
            
            i = 0
            while i < total_steps:
                step = execution_order[i]
                logger.info(f"🔄 Executando passo {i + 1}/{total_steps}: {step.label}")
                
                yield {
                    "current_step": i + 1,
                    "logs": [f"Executando passo {i + 1}/{total_steps}: {step.label}"]
                }
                
                # Se for um loop, executar o corpo do loop
                if step.type == NodeType.LOOP_FOR:
                    # Iniciar o loop
                    result = await self.execute_step_loop_for(step)
                    
                    if not result.get("success"):
                        logger.error(f"❌ Falha ao iniciar loop: {result.get('error', 'Erro desconhecido')}")
                        yield {
                            "error": result.get("error", "Erro desconhecido"),
                            "logs": result.get("logs", [])
                        }
                        return
                    
                    # Encontrar passos dentro do loop
                    loop_body_indices = self._find_loop_body(step.id, execution_order, edges)
                    
                    if not loop_body_indices:
                        logger.warning(f"⚠️ Nenhum passo encontrado dentro do loop {step.id}")
                        i += 1
                        continue
                    
                    logger.info(f"🔄 Loop iniciado: {len(loop_body_indices)} passos dentro do loop")
                    
                    # Executar loop até terminar
                    iteration = 0
                    while self.pandas_executor.should_continue_loop():
                        iteration += 1
                        logger.info(f"🔄 Iteração {iteration} do loop")
                        
                        # Avançar loop (define variável de iteração)
                        advance_result = self.pandas_executor.advance_loop()
                        if not advance_result.get("continue_loop", False):
                            break
                        
                        # Executar todos os passos dentro do loop
                        for loop_step_idx in loop_body_indices:
                            if loop_step_idx >= len(execution_order):
                                continue
                                
                            loop_step = execution_order[loop_step_idx]
                            logger.info(f"  ↳ Executando passo do loop: {loop_step.label}")
                            
                            yield {
                                "current_step": i + 1,
                                "logs": [f"Iteração {iteration} - {loop_step.label}"]
                            }
                            
                            # Executar passo dentro do loop
                            loop_result = await self._execute_step(loop_step)
                            
                            if not loop_result.get("success"):
                                logger.error(f"❌ Erro no passo do loop: {loop_result.get('error')}")
                                yield {
                                    "error": loop_result.get("error", "Erro desconhecido"),
                                    "logs": loop_result.get("logs", [])
                                }
                                return
                            
                            yield {
                                "current_step": i + 1,
                                "logs": loop_result.get("logs", []),
                                "results": {f"loop_iteration_{iteration}": "success"}
                            }
                            
                            await asyncio.sleep(0.3)
                        
                        # Verificar se loop deve continuar
                        if not self.pandas_executor.should_continue_loop():
                            logger.info(f"✅ Loop concluído após {iteration} iterações")
                            break
                    
                    # Avançar para próximo passo após o loop (pular corpo do loop)
                    if loop_body_indices:
                        i = max(loop_body_indices) + 1
                    else:
                        i += 1
                    continue
                
                # Executar passo normal
                result = await self._execute_step(step)
                
                # Enviar resultado do passo
                if result["success"]:
                    logger.info(f"✅ Passo {i + 1} concluído com sucesso")
                    yield {
                        "current_step": i + 1,
                        "logs": result.get("logs", []),
                        "results": {f"step_{i+1}": "success"}
                    }
                else:
                    logger.error(f"❌ Passo {i + 1} falhou: {result.get('error', 'Erro desconhecido')}")
                    yield {
                        "error": result.get("error", "Erro desconhecido"),
                        "logs": result.get("logs", [])
                    }
                    return
                
                # Pequena pausa entre passos
                await asyncio.sleep(0.5)
                i += 1
            
            logger.info("🎉 Fluxo executado com sucesso!")
            
        finally:
            # Não fechar automaticamente - apenas se houver bloco "Fechar Navegador"
            # self._cleanup_driver()
            pass
    
    async def _execute_step(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa um passo individual"""
        if step.type == NodeType.LOGIN:
            return await self.execute_step_login(step)
        elif step.type == NodeType.OPEN_SITE:
            return await self.execute_step_open_site(step)
        elif step.type == NodeType.CLICK_BUTTON:
            return await self.execute_step_click(step)
        elif step.type == NodeType.EXTRACT_TABLE:
            return await self.execute_step_input_text(step)
        elif step.type == NodeType.CAPTURE_TABLE:
            return await self.execute_step_capture_table(step)
        elif step.type == NodeType.WAIT:
            return await self.execute_step_wait(step)
        elif step.type == NodeType.SLEEP:
            return await self.execute_step_sleep(step)
        elif step.type == NodeType.SPREADSHEET:
            return await self.execute_step_spreadsheet(step)
        elif step.type == NodeType.VARIABLE:
            return await self.execute_step_variable(step)
        elif step.type == NodeType.LOOP_WHILE:
            return await self.execute_step_loop_while(step)
        elif step.type == NodeType.CONDITION:
            return await self.execute_step_condition(step)
        elif step.type == NodeType.SCHEDULE:
            return await self.execute_step_schedule(step)
        elif step.type == NodeType.EXECUTE_SCRIPT:
            return await self.execute_step_execute_script(step)
        elif step.type == NodeType.EXTRACT_TEXT:
            return await self.execute_step_extract_text(step)
        elif step.type == NodeType.TRANSFORM_COLUMN:
            return await self.pandas_executor.execute_step_transform_column(step)
        elif step.type == NodeType.GROUP_DATA:
            return await self.pandas_executor.execute_step_group_data(step)
        elif step.type == NodeType.EXECUTE_PYTHON:
            return await self.execute_step_python(step)
        elif step.type == NodeType.CLOSE_BROWSER:
            return await self.execute_step_close_browser(step)
        else:
            return {"success": False, "error": f"Tipo de passo não suportado: {step.type}"}
    
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
                    
            elif step.type == NodeType.OPEN_SITE:
                if not step.inputs.get('url'):
                    errors.append(f"Passo {step_num}: URL é obrigatória")
                    
            elif step.type == NodeType.CLICK_BUTTON:
                if not step.inputs.get('selector_value'):
                    errors.append(f"Passo {step_num}: Seletor é obrigatório")
                    
            elif step.type == NodeType.EXTRACT_TABLE:
                if not step.inputs.get('selector_value'):
                    errors.append(f"Passo {step_num}: Seletor é obrigatório")
                if not step.inputs.get('text_value'):
                    warnings.append(f"Passo {step_num}: Texto a inserir não configurado")
                    
            elif step.type == NodeType.CAPTURE_TABLE:
                if not step.inputs.get('selector_value'):
                    errors.append(f"Passo {step_num}: Seletor da tabela é obrigatório")
                if not step.inputs.get('variable_name'):
                    warnings.append(f"Passo {step_num}: Nome da variável não configurado")
                    
            elif step.type == NodeType.WAIT:
                wait_type = step.inputs.get('wait_type', 'time')
                if wait_type == 'time' and not step.inputs.get('duration'):
                    errors.append(f"Passo {step_num}: Duração é obrigatória para espera por tempo")
                elif wait_type != 'time' and not step.inputs.get('selector_value'):
                    errors.append(f"Passo {step_num}: Seletor é obrigatório para espera por elemento")
                    
            elif step.type == NodeType.SLEEP:
                duration = step.inputs.get('duration')
                if not duration:
                    errors.append(f"Passo {step_num}: Duração é obrigatória para pausa (sleep)")
                else:
                    try:
                        float(duration)
                    except ValueError:
                        errors.append(f"Passo {step_num}: Duração deve ser um número válido")
                        
            elif step.type == NodeType.SPREADSHEET:
                operation = step.inputs.get('operation', 'read')
                if operation in ['read', 'save'] and not step.inputs.get('file_path'):
                    errors.append(f"Passo {step_num}: Caminho do arquivo é obrigatório")
                if not step.inputs.get('variable_name'):
                    errors.append(f"Passo {step_num}: Nome da variável é obrigatório")
                    
            elif step.type == NodeType.VARIABLE:
                if not step.inputs.get('variable_name'):
                    errors.append(f"Passo {step_num}: Nome da variável é obrigatório")
                operation = step.inputs.get('operation', 'set')
                if operation == 'set' and not step.inputs.get('variable_value'):
                    warnings.append(f"Passo {step_num}: Valor da variável não configurado")
                    
            elif step.type == NodeType.LOOP_FOR:
                loop_type = step.inputs.get('loop_type', 'range')
                if loop_type == 'dataframe_rows' and not step.inputs.get('dataframe_variable'):
                    errors.append(f"Passo {step_num}: Variável da planilha é obrigatória")
                elif loop_type == 'range':
                    if not step.inputs.get('start_value') or not step.inputs.get('end_value'):
                        errors.append(f"Passo {step_num}: Valores inicial e final são obrigatórios")
                        
            elif step.type == NodeType.LOOP_WHILE:
                condition_type = step.inputs.get('condition_type', 'variable_comparison')
                if condition_type == 'variable_comparison' and not step.inputs.get('variable_name'):
                    errors.append(f"Passo {step_num}: Nome da variável é obrigatório para comparação")
                    
            elif step.type == NodeType.CONDITION:
                condition_type = step.inputs.get('condition_type', 'variable_comparison')
                if condition_type == 'variable_comparison' and not step.inputs.get('variable_name'):
                    errors.append(f"Passo {step_num}: Nome da variável é obrigatório para comparação")
                    
            elif step.type == NodeType.SCHEDULE:
                if not step.inputs.get('time'):
                    errors.append(f"Passo {step_num}: Horário é obrigatório")
                else:
                    time_str = step.inputs.get('time', '')
                    try:
                        hour, minute = map(int, time_str.split(':'))
                        if not (0 <= hour <= 23 and 0 <= minute <= 59):
                            errors.append(f"Passo {step_num}: Horário inválido (use HH:MM)")
                    except ValueError:
                        errors.append(f"Passo {step_num}: Formato de horário inválido (use HH:MM)")
            
            elif step.type == NodeType.CLOSE_BROWSER:
                pass # Nenhuma validação específica necessária
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }