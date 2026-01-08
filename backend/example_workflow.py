#!/usr/bin/env python3
"""
Exemplo de workflow completo usando planilhas e loops
Demonstra como processar dados de uma planilha e automatizar um site
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def exemplo_workflow_planilha():
    """
    Exemplo: Ler planilha com dados de usuários e preencher formulário
    
    Estrutura da planilha esperada:
    | Nome          | Email                | Telefone     |
    |---------------|---------------------|--------------|
    | João Silva    | joao@email.com      | 11999999999  |
    | Maria Santos  | maria@email.com     | 11888888888  |
    """
    
    # 1. Ler planilha
    print("📊 Carregando planilha...")
    df = pd.read_excel("dados_usuarios.xlsx")
    print(f"✅ Planilha carregada: {len(df)} usuários")
    print(f"Colunas: {', '.join(df.columns.tolist())}")
    
    # 2. Inicializar navegador
    print("🌐 Iniciando navegador...")
    driver = webdriver.Chrome()
    
    try:
        # 3. Navegar para o site
        driver.get("https://exemplo.com/cadastro")
        driver.maximize_window()
        
        # 4. Loop pelas linhas da planilha
        print("🔄 Iniciando processamento dos usuários...")
        
        for index, row in df.iterrows():
            print(f"\n--- Processando usuário {index + 1}/{len(df)} ---")
            
            # Obter dados da linha atual
            nome = row["Nome"]
            email = row["Email"]
            telefone = row["Telefone"]
            
            print(f"👤 Nome: {nome}")
            print(f"📧 Email: {email}")
            print(f"📱 Telefone: {telefone}")
            
            # 5. Preencher formulário
            try:
                # Campo nome
                campo_nome = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "nome"))
                )
                campo_nome.clear()
                campo_nome.send_keys(nome)
                
                # Campo email
                campo_email = driver.find_element(By.ID, "email")
                campo_email.clear()
                campo_email.send_keys(email)
                
                # Campo telefone
                campo_telefone = driver.find_element(By.ID, "telefone")
                campo_telefone.clear()
                campo_telefone.send_keys(telefone)
                
                # Clicar no botão de cadastro
                botao_cadastro = driver.find_element(By.ID, "btn_cadastrar")
                botao_cadastro.click()
                
                # Aguardar processamento
                time.sleep(2)
                
                # Verificar se deu certo
                try:
                    sucesso = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "sucesso"))
                    )
                    print("✅ Usuário cadastrado com sucesso!")
                    
                    # Atualizar planilha com status
                    df.at[index, "Status"] = "Cadastrado"
                    
                except:
                    print("❌ Erro no cadastro")
                    df.at[index, "Status"] = "Erro"
                
                # Voltar para o formulário (se necessário)
                driver.get("https://exemplo.com/cadastro")
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Erro ao processar usuário: {str(e)}")
                df.at[index, "Status"] = f"Erro: {str(e)}"
                continue
        
        # 6. Salvar planilha com resultados
        print("\n💾 Salvando resultados...")
        df.to_excel("dados_usuarios_processados.xlsx", index=False)
        print("✅ Planilha salva com status de processamento")
        
        # 7. Relatório final
        total_usuarios = len(df)
        cadastrados = len(df[df["Status"] == "Cadastrado"])
        erros = total_usuarios - cadastrados
        
        print(f"\n📊 RELATÓRIO FINAL:")
        print(f"Total de usuários: {total_usuarios}")
        print(f"Cadastrados com sucesso: {cadastrados}")
        print(f"Erros: {erros}")
        print(f"Taxa de sucesso: {(cadastrados/total_usuarios)*100:.1f}%")
        
    finally:
        driver.quit()
        print("🏁 Processamento concluído!")

def criar_planilha_exemplo():
    """Cria uma planilha de exemplo para testar"""
    dados = {
        "Nome": ["João Silva", "Maria Santos", "Pedro Costa", "Ana Oliveira"],
        "Email": ["joao@email.com", "maria@email.com", "pedro@email.com", "ana@email.com"],
        "Telefone": ["11999999999", "11888888888", "11777777777", "11666666666"]
    }
    
    df = pd.DataFrame(dados)
    df.to_excel("dados_usuarios.xlsx", index=False)
    print("✅ Planilha de exemplo criada: dados_usuarios.xlsx")

if __name__ == "__main__":
    print("🚀 Exemplo de Workflow com Planilhas")
    print("="*50)
    
    # Criar planilha de exemplo
    criar_planilha_exemplo()
    
    # Executar workflow
    exemplo_workflow_planilha()