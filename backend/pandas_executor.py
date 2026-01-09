#!/usr/bin/env python3
"""
Executor para operações com Pandas e estruturas de controle
Gerencia planilhas, loops e variáveis
"""

import pandas as pd
import os
import asyncio
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path

from models import FlowExecutionStep, NodeType

logger = logging.getLogger(__name__)

class PandasExecutor:
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.loop_stack: List[Dict[str, Any]] = []
        
    def reset_state(self):
        """Reseta o estado do executor"""
        self.variables.clear()
        self.dataframes.clear()
        self.loop_stack.clear()
    
    def _get_safe_path(self, file_path: str) -> str:
        """
        Garante que o caminho do arquivo esteja dentro de workflows/sheets.
        Permite subpastas definidas pelo usuário.
        """
        # Base: DATA_DIR/workflows/sheets
        data_dir = os.getenv('DATA_DIR', '/app/data')
        sheets_dir = os.path.join(data_dir, 'workflows', 'sheets')
        os.makedirs(sheets_dir, exist_ok=True)
        
        # Normalizar caminho de entrada
        # Remove caracteres perigosos e normaliza barras
        clean_path = file_path.strip().replace('\\', '/')
        
        # Se o usuário passar um caminho absoluto, pegamos apenas o relativo à "sheets" se possível,
        # ou forçamos ser relativo removendo o drive/root.
        # Simplificação: tratamos tudo como relativo à sheets_dir.
        # Removemos referências a diretórios pais (..)
        clean_path = clean_path.replace('..', '')
        while clean_path.startswith('/'):
            clean_path = clean_path[1:]
        
        # Se o caminho for vazio após limpeza (ex: só tinha barra), usa padrão
        if not clean_path:
            clean_path = "dados.xlsx"

        safe_path = os.path.join(sheets_dir, clean_path)
        
        # Garantir que o diretório pai do arquivo exista
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
            
        return safe_path

    async def execute_step_spreadsheet(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa operações com planilhas"""
        try:
            inputs = step.inputs
            logs = []
            
            operation = inputs.get('operation', 'read')
            raw_file_path = inputs.get('file_path', 'dados.xlsx')
            sheet_name = inputs.get('sheet_name', 'Sheet1')
            variable_name = inputs.get('variable_name', 'df')
            
            # Resolver caminho seguro
            file_path = self._get_safe_path(raw_file_path)
            logs.append(f"Caminho do arquivo resolvido: {file_path}")
            
            logger.info(f"📊 Operação de planilha: {operation} em {file_path}")
            
            if operation == 'read':
                # Ler planilha
                if not os.path.exists(file_path):
                    return {"success": False, "error": f"Arquivo não encontrado: {file_path} (original: {raw_file_path})"}
                
                if file_path.lower().endswith('.csv'):
                    df = pd.read_csv(file_path)
                    logs.append(f"CSV carregado: {file_path}")
                else:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    logs.append(f"Excel carregado: {file_path}, aba: {sheet_name}")
                
                self.dataframes[variable_name] = df
                self.variables[variable_name] = df
                
                logs.append(f"Planilha armazenada na variável: {variable_name}")
                logs.append(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
                logs.append(f"Colunas: {', '.join(df.columns.tolist())}")
                
                logger.info(f"✅ Planilha carregada: {df.shape[0]} linhas, {df.shape[1]} colunas")
                
            elif operation == 'create':
                # Criar nova planilha
                columns = inputs.get('columns', 'Coluna1').split(',')
                columns = [col.strip() for col in columns]
                
                df = pd.DataFrame(columns=columns)
                self.dataframes[variable_name] = df
                self.variables[variable_name] = df
                
                logs.append(f"Nova planilha criada: {variable_name}")
                logs.append(f"Colunas: {', '.join(columns)}")
                
                logger.info(f"✅ Nova planilha criada: {variable_name}")
                
            elif operation == 'write':
                # Escrever dados na planilha
                if variable_name not in self.dataframes:
                    return {"success": False, "error": f"Planilha não encontrada: {variable_name}"}
                
                # Implementar lógica de escrita baseada nos inputs
                logs.append(f"Dados escritos na planilha: {variable_name}")
                
            elif operation == 'save':
                # Salvar planilha
                if variable_name not in self.dataframes:
                    return {"success": False, "error": f"Planilha não encontrada: {variable_name}"}
                
                df = self.dataframes[variable_name]
                
                # Criar diretório se não existir (garantia redundante mas segura)
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Opções adicionais de salvamento
                include_index = inputs.get('include_index', 'false') == 'true'
                header = inputs.get('include_header', 'true') != 'false'  # Padrão True
                
                if file_path.lower().endswith('.csv'):
                    df.to_csv(file_path, index=include_index, header=header)
                    logs.append(f"CSV salvo: {file_path}")
                else:
                    # Para Excel, pode adicionar colunas extras como no SISREG.py
                    df.to_excel(file_path, sheet_name=sheet_name, index=include_index, header=header)
                    
                    # Se especificado, adicionar colunas extras (como competência e nome_unidade)
                    extra_column_name = inputs.get('extra_column_name', '')
                    extra_column_value = inputs.get('extra_column_value', '')
                    extra_column_position = inputs.get('extra_column_position', '1')  # 1 = primeira coluna
                    
                    if extra_column_name and extra_column_value:
                        try:
                            from openpyxl import load_workbook
                            wb = load_workbook(file_path)
                            ws = wb.active
                            
                            # Adicionar coluna extra
                            col_pos = int(extra_column_position)
                            for row in range(2, ws.max_row + 1):  # Começa da linha 2
                                cell = ws.cell(row=row, column=col_pos)
                                if cell.value:  # Se a célula tem conteúdo
                                    cell.value = extra_column_value
                            
                            wb.save(file_path)
                            logs.append(f"Coluna extra '{extra_column_name}' adicionada")
                        except Exception as e:
                            logs.append(f"Aviso: Não foi possível adicionar coluna extra: {str(e)}")
                    
                    logs.append(f"Excel salvo: {file_path}, aba: {sheet_name}")
                
                logger.info(f"✅ Planilha salva: {file_path}")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro na operação de planilha: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro na planilha: {str(e)}"]}
    
    async def execute_step_group_data(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa agrupamento de dados no DataFrame"""
        try:
            inputs = step.inputs
            logs = []
            
            dataframe_variable = inputs.get('dataframe_variable', 'df')
            group_by_column = inputs.get('group_by_column', '')
            # Formato esperado: "col1:agg1,col2:agg2" ex: "id:size,valor:sum"
            aggregations_str = inputs.get('aggregations', '')
            output_variable = inputs.get('output_variable', 'df_grouped')
            
            if dataframe_variable not in self.dataframes:
                return {"success": False, "error": f"DataFrame não encontrado: {dataframe_variable}"}
            
            df = self.dataframes[dataframe_variable]
            
            if group_by_column not in df.columns:
                 return {"success": False, "error": f"Coluna de agrupamento não encontrada: {group_by_column}"}
            
            logger.info(f"🔢 Agrupando por: {group_by_column}")
            logs.append(f"Agrupando DataFrame '{dataframe_variable}' por '{group_by_column}'")

            # Processar agregações
            agg_dict = {}
            if aggregations_str:
                for agg_item in aggregations_str.split(','):
                    if ':' in agg_item:
                        col, func = agg_item.split(':')
                        col = col.strip()
                        func = func.strip()
                        
                        # Tratamento especial para 'size' que não precisa de coluna específica ou usa a de agrupamento
                        if func == 'size':
                            agg_dict[group_by_column] = 'size'
                        elif col in df.columns or col == group_by_column: # Permitir agregar a propria coluna de grupo
                            # Suporte a funções lambda simples se necessário, mas por segurança manteremos strings padrão
                            # Para listas únicas, usaremos uma string especial
                            if func == 'unique_list':
                                agg_dict[col] = lambda x: sorted(list(set(x)))
                            elif func == 'unique_list_limited':
                                # Limita a 4 itens como no script original
                                agg_dict[col] = lambda x: sorted(list(set(x)))[:4]
                            else:
                                agg_dict[col] = func
                        else:
                             logs.append(f"Aviso: Coluna '{col}' para agregação não encontrada, ignorando.")
            
            if not agg_dict:
                 agg_dict[group_by_column] = 'size' # Default

            # Realizar agrupamento
            # Se unique_list for usada, o pandas pode reclamar de lambda na serialização em alguns contextos,
            # mas aqui estamos em memória.
            grouped = df.groupby(group_by_column).agg(agg_dict)
            
            # Renomear colunas se necessário (opcional, pode ser feito em passo separado ou automático)
            # Por padrão o pandas mantém o nome da coluna se agg for unica, ou cria MultiIndex
            # Vamos resetar o index para transformar o grupo em coluna novamente
            result_df = grouped.reset_index()
            
            self.dataframes[output_variable] = result_df
            self.variables[output_variable] = result_df
            
            logs.append(f"Agrupamento concluído. Novo DataFrame: {output_variable}")
            logs.append(f"Linhas resultantes: {len(result_df)}")
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro no agrupamento: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro no agrupamento: {str(e)}"]}

    async def execute_step_transform_column(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Transforma uma coluna do DataFrame"""
        try:
            inputs = step.inputs
            logs = []
            
            dataframe_variable = inputs.get('dataframe_variable', 'df')
            column_name = inputs.get('column_name', '')
            # Tipos: 'first_letter_upper', 'parse_list', 'custom_lambda'
            transformation_type = inputs.get('transformation_type', 'first_letter_upper') 
            new_column_name = inputs.get('new_column_name', '') # Se vazio, substitui a original
            
            if dataframe_variable not in self.dataframes:
                return {"success": False, "error": f"DataFrame não encontrado: {dataframe_variable}"}
            
            df = self.dataframes[dataframe_variable]
            target_col_name = new_column_name if new_column_name else column_name
            
            if column_name not in df.columns and transformation_type != 'create_empty':
                return {"success": False, "error": f"Coluna alvo não encontrada: {column_name}"}

            logger.info(f"✨ Transformando coluna: {column_name} -> {transformation_type}")
            
            if transformation_type == 'first_letter_upper':
                # Pega a primeira letra e deixa maiúscula
                df[target_col_name] = df[column_name].astype(str).str[0].str.upper()
                logs.append(f"Transformação 'first_letter_upper' aplicada em '{column_name}'")
                
            elif transformation_type == 'parse_list':
                # Converte string representativa de lista em lista real
                import ast
                def safe_eval(x):
                    try:
                        if isinstance(x, list): return x
                        return ast.literal_eval(x)
                    except:
                        return []
                df[target_col_name] = df[column_name].apply(safe_eval)
                logs.append(f"Transformação 'parse_list' aplicada em '{column_name}'")
                
            elif transformation_type == 'limit_list':
                # Limita lista a N itens
                limit = int(inputs.get('limit', 4))
                df[target_col_name] = df[column_name].apply(lambda x: x[:limit] if isinstance(x, list) else x)
                logs.append(f"Transformação 'limit_list' (max {limit}) aplicada em '{column_name}'")
                
            elif transformation_type == 'to_string':
                # Converte para string
                df[target_col_name] = df[column_name].astype(str)
                 
            self.dataframes[dataframe_variable] = df # Atualiza ref (caso tenha mudado algo estrutural, em pandas geralmente é inplace ou ref direta)
            
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro na transformação: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro na transformação: {str(e)}"]}

    async def execute_step_variable(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa operações com variáveis"""
        try:
            inputs = step.inputs
            logs = []
            
            operation = inputs.get('operation', 'set')
            variable_name = inputs.get('variable_name', 'variavel')
            
            logger.info(f"🔢 Operação de variável: {operation}")
            
            if operation == 'set':
                # Definir valor da variável
                variable_value = inputs.get('variable_value', '')
                self.variables[variable_name] = variable_value
                logs.append(f"Variável definida: {variable_name} = {variable_value}")
                
            elif operation == 'get_cell':
                # Obter valor de célula da planilha
                dataframe_variable = inputs.get('dataframe_variable', 'df')
                row_variable = inputs.get('row_variable', 'row')
                column_name = inputs.get('column_name', 'Coluna1')
                
                if row_variable not in self.variables:
                    return {"success": False, "error": f"Variável de linha não encontrada: {row_variable}"}
                
                row_data = self.variables[row_variable]
                if isinstance(row_data, pd.Series) and column_name in row_data:
                    cell_value = row_data[column_name]
                    self.variables[variable_name] = cell_value
                    logs.append(f"Valor da célula obtido: {variable_name} = {cell_value}")
                else:
                    return {"success": False, "error": f"Coluna não encontrada: {column_name}"}
                
            elif operation == 'increment':
                # Incrementar variável
                increment_value = float(inputs.get('increment_value', 1))
                current_value = self.variables.get(variable_name, 0)
                
                try:
                    new_value = float(current_value) + increment_value
                    self.variables[variable_name] = new_value
                    logs.append(f"Variável incrementada: {variable_name} = {new_value}")
                except ValueError:
                    return {"success": False, "error": f"Não é possível incrementar variável não numérica: {variable_name}"}
            
            elif operation == 'concatenate':
                # Concatenar texto
                text_to_add = inputs.get('text_to_add', '')
                current_value = str(self.variables.get(variable_name, ''))
                new_value = current_value + text_to_add
                self.variables[variable_name] = new_value
                logs.append(f"Texto concatenado: {variable_name} = {new_value}")
            
            elif operation == 'get_list_item':
                # Obter item de uma lista pelo índice
                list_variable = inputs.get('list_variable', '')
                index_variable = inputs.get('index_variable', '')
                output_variable = inputs.get('output_variable', 'list_item')
                
                if list_variable not in self.variables:
                     # Se variável não existe, tenta ver se é um literal (embora raro para lista)
                     return {"success": False, "error": f"Variável de lista não encontrada: {list_variable}"}
                
                lista = self.variables[list_variable]
                if not isinstance(lista, list):
                     return {"success": False, "error": f"Variável '{list_variable}' não é uma lista. Tipo: {type(lista)}"}
                
                # Obter índice
                if index_variable in self.variables:
                    idx = int(self.variables[index_variable])
                else:
                    try:
                        idx = int(index_variable)
                    except:
                         return {"success": False, "error": f"Índice inválido: {index_variable}"}
                
                if 0 <= idx < len(lista):
                    self.variables[output_variable] = lista[idx]
                    logs.append(f"Item {idx} obtido da lista: {lista[idx]}")
                else:
                    # Índice fora dos limites - retorna string vazia ou erro?
                    # Para nosso caso de uso, melhor retornar vazio para indicar fim ou inexistencia sem crashar o loop fixo
                    self.variables[output_variable] = ""
                    logs.append(f"Aviso: Índice {idx} fora dos limites da lista (len={len(lista)}). Retornando vazio.")

            
            logger.info(f"✅ Operação de variável concluída: {variable_name}")
            return {"success": True, "logs": logs}
            
        except Exception as e:
            logger.error(f"❌ Erro na operação de variável: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro na variável: {str(e)}"]}
    
    async def execute_step_loop_for(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Inicia um loop for"""
        try:
            inputs = step.inputs
            logs = []
            
            loop_type = inputs.get('loop_type', 'range')
            max_iterations = int(inputs.get('max_iterations', 1000))
            
            logger.info(f"🔄 Iniciando loop for: {loop_type}")
            
            if loop_type == 'dataframe_rows':
                # Loop pelas linhas da planilha
                dataframe_variable = inputs.get('dataframe_variable', 'df')
                row_variable = inputs.get('row_variable', 'row')
                
                if dataframe_variable not in self.dataframes:
                    return {"success": False, "error": f"Planilha não encontrada: {dataframe_variable}"}
                
                df = self.dataframes[dataframe_variable]
                
                # Preparar dados do loop
                loop_data = {
                    'type': 'dataframe_rows',
                    'dataframe': df,
                    'row_variable': row_variable,
                    'current_index': 0,
                    'total_rows': len(df),
                    'max_iterations': max_iterations
                }
                
                self.loop_stack.append(loop_data)
                logs.append(f"Loop iniciado: {len(df)} linhas para processar")
                
            elif loop_type == 'range':
                # Loop numérico
                start_value = int(inputs.get('start_value', 0))
                end_value = int(inputs.get('end_value', 10))
                step_value = int(inputs.get('step_value', 1))
                row_variable = inputs.get('row_variable', 'i')
                
                loop_data = {
                    'type': 'range',
                    'start': start_value,
                    'end': end_value,
                    'step': step_value,
                    'current': start_value - step_value,  # Começar antes para que advance_loop funcione corretamente
                    'row_variable': row_variable,
                    'max_iterations': max_iterations
                }
                
                self.loop_stack.append(loop_data)
                logs.append(f"Loop numérico iniciado: {start_value} até {end_value} (variável: {row_variable})")
            
            logger.info(f"✅ Loop for configurado")
            return {"success": True, "logs": logs, "loop_started": True}
            
        except Exception as e:
            logger.error(f"❌ Erro no loop for: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro no loop: {str(e)}"]}
    
    def should_continue_loop(self) -> bool:
        """Verifica se o loop atual deve continuar"""
        if not self.loop_stack:
            return False
        
        current_loop = self.loop_stack[-1]
        
        if current_loop['type'] == 'dataframe_rows':
            return current_loop['current_index'] < current_loop['total_rows']
        elif current_loop['type'] == 'range':
            # Verificar se ainda há iterações
            next_value = current_loop['current'] + current_loop['step']
            return next_value <= current_loop['end']
        
        return False
    
    def advance_loop(self) -> Dict[str, Any]:
        """Avança para a próxima iteração do loop"""
        if not self.loop_stack:
            return {"success": False, "error": "Nenhum loop ativo"}
        
        current_loop = self.loop_stack[-1]
        logs = []
        
        if current_loop['type'] == 'dataframe_rows':
            # Avançar para próxima linha
            df = current_loop['dataframe']
            index = current_loop['current_index']
            row_variable = current_loop['row_variable']
            
            if index < len(df):
                row_data = df.iloc[index]
                self.variables[row_variable] = row_data
                self.variables['row_index'] = index
                
                current_loop['current_index'] += 1
                logs.append(f"Processando linha {index + 1}/{len(df)}")
                
                return {"success": True, "logs": logs, "continue_loop": True}
            else:
                # Loop terminado
                self.loop_stack.pop()
                logs.append("Loop de linhas concluído")
                return {"success": True, "logs": logs, "continue_loop": False}
        
        elif current_loop['type'] == 'range':
            # Avançar contador
            current_value = current_loop['current']
            row_variable = current_loop.get('row_variable', 'i')
            self.variables[row_variable] = current_value
            self.variables['i'] = current_value  # Manter compatibilidade
            
            logs.append(f"Iteração: {current_value}")
            
            # Avançar para próxima iteração ANTES de verificar se terminou
            current_loop['current'] += current_loop['step']
            
            if current_loop['current'] > current_loop['end']:
                # Loop terminado
                self.loop_stack.pop()
                logs.append("Loop numérico concluído")
                return {"success": True, "logs": logs, "continue_loop": False}
            else:
                return {"success": True, "logs": logs, "continue_loop": True}
        
        return {"success": False, "error": "Tipo de loop não suportado"}
    
    def get_variable_value(self, variable_name: str, default_value: Any = None) -> Any:
        """Obtém valor de uma variável"""
        return self.variables.get(variable_name, default_value)
    
    def substitute_variables(self, text: str) -> str:
        """Substitui variáveis no texto usando formato ${variavel}"""
        import re
        
        def replace_var(match):
            var_name = match.group(1)
            return str(self.variables.get(var_name, f"${{{var_name}}}"))
        
        return re.sub(r'\$\{([^}]+)\}', replace_var, text)
    
    async def execute_step_condition(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de condição (if/else)"""
        try:
            inputs = step.inputs
            logs = []
            
            condition_type = inputs.get('condition_type', 'variable_comparison')
            
            logger.info(f"🌿 Avaliando condição: {condition_type}")
            
            condition_result = False
            
            if condition_type == 'variable_comparison':
                # Comparar variável
                variable_name = inputs.get('variable_name', '')
                comparison_operator = inputs.get('comparison_operator', '==')
                comparison_value = inputs.get('comparison_value', '')
                
                if variable_name not in self.variables:
                    logs.append(f"⚠️ Variável não encontrada: {variable_name}")
                    condition_result = False
                else:
                    var_value = self.variables[variable_name]
                    
                    # Tentar converter valores para comparação
                    try:
                        # Se ambos são números, comparar como números
                        var_num = float(var_value)
                        comp_num = float(comparison_value)
                        
                        if comparison_operator == '==':
                            condition_result = var_num == comp_num
                        elif comparison_operator == '!=':
                            condition_result = var_num != comp_num
                        elif comparison_operator == '<':
                            condition_result = var_num < comp_num
                        elif comparison_operator == '<=':
                            condition_result = var_num <= comp_num
                        elif comparison_operator == '>':
                            condition_result = var_num > comp_num
                        elif comparison_operator == '>=':
                            condition_result = var_num >= comp_num
                            
                    except ValueError:
                        # Comparar como strings
                        var_str = str(var_value)
                        comp_str = str(comparison_value)
                        
                        if comparison_operator == '==':
                            condition_result = var_str == comp_str
                        elif comparison_operator == '!=':
                            condition_result = var_str != comp_str
                        elif comparison_operator == 'in':
                            condition_result = comp_str in var_str
                        elif comparison_operator == 'not in':
                            condition_result = comp_str not in var_str
                        else:
                            return {"success": False, "error": f"Operador não suportado para strings: {comparison_operator}"}
                    
                    logs.append(f"Comparação: {var_value} {comparison_operator} {comparison_value} = {condition_result}")
            
            elif condition_type == 'element_exists':
                # Verificar se elemento existe (seria implementado com Selenium)
                logs.append("Verificação de elemento não implementada neste contexto")
                condition_result = False
                
            elif condition_type == 'text_contains':
                # Verificar se texto contém substring
                text_source = inputs.get('text_source', '')
                search_text = inputs.get('search_text', '')
                
                if text_source in self.variables:
                    source_text = str(self.variables[text_source])
                    condition_result = search_text in source_text
                    logs.append(f"Texto '{search_text}' {'encontrado' if condition_result else 'não encontrado'} em '{text_source}'")
                else:
                    logs.append(f"⚠️ Variável de texto não encontrada: {text_source}")
                    condition_result = False
            
            elif condition_type == 'custom':
                # Condição personalizada em Python
                custom_condition = inputs.get('custom_condition', 'True')
                try:
                    # Criar contexto seguro com as variáveis
                    safe_builtins = {
                        'int': int, 'float': float, 'str': str, 'bool': bool,
                        'list': list, 'dict': dict, 'len': len, 'range': range,
                        'abs': abs, 'round': round, 'min': min, 'max': max, 'sum': sum
                    }
                    safe_globals = {"__builtins__": safe_builtins}
                    safe_locals = self.variables.copy()
                    safe_locals['variables'] = self.variables  # Permitir acesso explícito ao dict variables
                    
                    condition_result = bool(eval(custom_condition, safe_globals, safe_locals))
                    logs.append(f"Condição personalizada: {custom_condition} = {condition_result}")
                except Exception as e:
                    return {"success": False, "error": f"Erro na condição personalizada: {str(e)}"}
            
            # Armazenar resultado da condição para uso posterior
            self.variables['_last_condition_result'] = condition_result
            
            logger.info(f"✅ Condição avaliada: {condition_result}")
            logs.append(f"Resultado da condição: {condition_result}")
            
            return {
                "success": True, 
                "logs": logs,
                "condition_result": condition_result
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na condição: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro na condição: {str(e)}"]}
    
    async def execute_step_loop_while(self, step: FlowExecutionStep) -> Dict[str, Any]:
        """Executa passo de loop while"""
        try:
            inputs = step.inputs
            logs = []
            
            condition_type = inputs.get('condition_type', 'variable_comparison')
            max_iterations = int(inputs.get('max_iterations', 100))
            
            logger.info(f"🔁 Iniciando loop while: {condition_type}")
            
            # Configurar dados do loop while
            loop_data = {
                'type': 'while',
                'condition_type': condition_type,
                'condition_inputs': inputs,
                'current_iteration': 0,
                'max_iterations': max_iterations
            }
            
            self.loop_stack.append(loop_data)
            logs.append(f"Loop while iniciado (máximo {max_iterations} iterações)")
            
            logger.info(f"✅ Loop while configurado")
            return {"success": True, "logs": logs, "loop_started": True}
            
        except Exception as e:
            logger.error(f"❌ Erro no loop while: {str(e)}")
            return {"success": False, "error": str(e), "logs": [f"Erro no loop while: {str(e)}"]}
    
    def should_continue_while_loop(self) -> Dict[str, Any]:
        """Verifica se o loop while atual deve continuar"""
        if not self.loop_stack:
            return {"continue": False, "error": "Nenhum loop ativo"}
        
        current_loop = self.loop_stack[-1]
        
        if current_loop['type'] != 'while':
            return {"continue": False, "error": "Loop atual não é do tipo while"}
        
        # Verificar limite de iterações
        if current_loop['current_iteration'] >= current_loop['max_iterations']:
            self.loop_stack.pop()
            return {"continue": False, "reason": "Limite de iterações atingido"}
        
        # Avaliar condição
        condition_inputs = current_loop['condition_inputs']
        condition_type = current_loop['condition_type']
        
        try:
            condition_result = False
            
            if condition_type == 'variable_comparison':
                variable_name = condition_inputs.get('variable_name', '')
                comparison_operator = condition_inputs.get('comparison_operator', '==')
                comparison_value = condition_inputs.get('comparison_value', '')
                
                if variable_name in self.variables:
                    var_value = self.variables[variable_name]
                    
                    try:
                        var_num = float(var_value)
                        comp_num = float(comparison_value)
                        
                        if comparison_operator == '<':
                            condition_result = var_num < comp_num
                        elif comparison_operator == '<=':
                            condition_result = var_num <= comp_num
                        elif comparison_operator == '>':
                            condition_result = var_num > comp_num
                        elif comparison_operator == '>=':
                            condition_result = var_num >= comp_num
                        elif comparison_operator == '==':
                            condition_result = var_num == comp_num
                        elif comparison_operator == '!=':
                            condition_result = var_num != comp_num
                            
                    except ValueError:
                        var_str = str(var_value)
                        comp_str = str(comparison_value)
                        
                        if comparison_operator == '==':
                            condition_result = var_str == comp_str
                        elif comparison_operator == '!=':
                            condition_result = var_str != comp_str
            
            elif condition_type == 'custom':
                custom_condition = condition_inputs.get('custom_condition', 'False')
                safe_builtins = {
                    'int': int, 'float': float, 'str': str, 'bool': bool,
                    'list': list, 'dict': dict, 'len': len, 'range': range,
                    'abs': abs, 'round': round, 'min': min, 'max': max, 'sum': sum
                }
                safe_globals = {"__builtins__": safe_builtins}
                safe_locals = self.variables.copy()
                safe_locals['variables'] = self.variables  # Permitir acesso explícito ao dict variables
                condition_result = bool(eval(custom_condition, safe_globals, safe_locals))
            
            # Incrementar contador de iterações
            current_loop['current_iteration'] += 1
            
            if not condition_result:
                # Condição falsa, terminar loop
                self.loop_stack.pop()
                return {"continue": False, "reason": "Condição falsa"}
            
            return {"continue": True, "iteration": current_loop['current_iteration']}
            
        except Exception as e:
            self.loop_stack.pop()
            return {"continue": False, "error": f"Erro ao avaliar condição: {str(e)}"}