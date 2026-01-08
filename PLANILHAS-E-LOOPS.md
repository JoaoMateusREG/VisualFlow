# 📊 Guia: Planilhas e Loops na Automação Visual

Este guia explica como usar os novos blocos de **Planilhas (Pandas)** e **Estruturas de Controle (Loops)** para criar automações mais poderosas.

## 🎯 Caso de Uso Principal

**Cenário**: Você tem uma planilha Excel/CSV com dados (ex: nomes, emails, telefones) e precisa preencher esses dados em um site, linha por linha.

**Exemplo prático**:
- Planilha com 100 clientes
- Para cada cliente: preencher nome em um campo, clicar em botão, preencher email em popup
- Repetir até processar todos os clientes

## 🧩 Novos Blocos Disponíveis

### 📊 Bloco: Planilha (Excel/CSV)
**Cor**: Verde esmeralda  
**Operações**:
- **Ler Planilha**: Carrega dados de arquivo Excel/CSV
- **Criar Planilha**: Cria nova planilha vazia
- **Salvar Planilha**: Salva dados em arquivo

**Configurações**:
- **Caminho do Arquivo**: `C:/dados/clientes.xlsx` ou `dados.csv`
- **Nome da Aba**: `Sheet1` (apenas para Excel)
- **Nome da Variável**: `df_clientes` (como referenciar nos outros blocos)

### 🔄 Bloco: Loop For (Repetir)
**Cor**: Ciano  
**Tipos de Loop**:
- **Linhas da Planilha**: Processa cada linha de uma planilha
- **Intervalo Numérico**: Loop de 0 a 10, por exemplo
- **Lista de Valores**: Loop por lista personalizada

**Configurações para Planilha**:
- **Variável da Planilha**: `df_clientes`
- **Variável da Linha Atual**: `linha_atual`
- **Máximo de Iterações**: `1000` (segurança)

### 🔢 Bloco: Variável
**Cor**: Âmbar  
**Operações**:
- **Definir Valor**: `minha_var = "valor"`
- **Obter Célula da Planilha**: Pega valor de uma coluna da linha atual
- **Incrementar**: Soma valor à variável
- **Concatenar Texto**: Adiciona texto à variável

**Para obter dados da planilha**:
- **Variável da Planilha**: `df_clientes`
- **Variável da Linha**: `linha_atual`
- **Nome da Coluna**: `Nome` (exatamente como na planilha)

### ⏱️ Bloco: Pausa (Sleep)
**Cor**: Índigo  
**Uso**: Pausas simples com `time.sleep()`
- **Duração**: `2.5` segundos
- **Descrição**: Comentário opcional

## 🔧 Como Usar Variáveis nos Campos

Você pode usar variáveis em qualquer campo de texto usando a sintaxe `${nome_da_variavel}`:

**Exemplos**:
- Campo de texto: `${nome_cliente}`
- URL dinâmica: `https://site.com/user/${user_id}`
- Seletor dinâmico: `#user_${linha_atual.ID}`

## 📋 Workflow Exemplo: Processar Planilha de Clientes

### Estrutura da Planilha (`clientes.xlsx`):
```
| Nome          | Email                | Telefone     |
|---------------|---------------------|--------------|
| João Silva    | joao@email.com      | 11999999999  |
| Maria Santos  | maria@email.com     | 11888888888  |
| Pedro Costa   | pedro@email.com     | 11777777777  |
```

### Sequência de Blocos:

1. **📊 Planilha**: 
   - Operação: `Ler Planilha`
   - Arquivo: `C:/dados/clientes.xlsx`
   - Variável: `df_clientes`

2. **🌐 Login**: 
   - URL: `https://sistema.com/login`
   - Fazer login no sistema

3. **🔄 Loop For**:
   - Tipo: `Linhas da Planilha`
   - Planilha: `df_clientes`
   - Linha Atual: `linha_atual`

4. **🔢 Variável** (Nome):
   - Operação: `Obter Célula da Planilha`
   - Planilha: `df_clientes`
   - Linha: `linha_atual`
   - Coluna: `Nome`
   - Variável: `nome_cliente`

5. **🔢 Variável** (Email):
   - Operação: `Obter Célula da Planilha`
   - Planilha: `df_clientes`
   - Linha: `linha_atual`
   - Coluna: `Email`
   - Variável: `email_cliente`

6. **📝 Inserir Texto**:
   - Seletor: `#campo_nome`
   - Texto: `${nome_cliente}`

7. **🖱️ Clicar Botão**:
   - Seletor: `#btn_abrir_popup`

8. **⏱️ Aguardar Elemento**:
   - Seletor: `#popup_email`
   - Aguardar popup aparecer

9. **📝 Inserir Texto**:
   - Seletor: `#campo_email_popup`
   - Texto: `${email_cliente}`

10. **🖱️ Clicar Botão**:
    - Seletor: `#btn_salvar_popup`

11. **⏱️ Pausa**:
    - Duração: `2`
    - Descrição: `Aguardar processamento`

## 🐍 Código Python Gerado

O sistema gera automaticamente código Python como este:

```python
import pandas as pd
from selenium import webdriver
# ... outros imports

# Variáveis globais
variables = {}
dataframes = {}

# Inicializar driver
driver = webdriver.Chrome()

try:
    # Ler planilha
    df_clientes = pd.read_excel("C:/dados/clientes.xlsx")
    dataframes["df_clientes"] = df_clientes
    print(f"Planilha carregada: {len(df_clientes)} linhas")
    
    # Login
    driver.get("https://sistema.com/login")
    # ... código de login
    
    # Loop pelas linhas
    for index, linha_atual in df_clientes.iterrows():
        variables["linha_atual"] = linha_atual
        print(f"Processando linha {index + 1}")
        
        # Obter nome da linha atual
        nome_cliente = linha_atual["Nome"]
        variables["nome_cliente"] = nome_cliente
        
        # Obter email da linha atual
        email_cliente = linha_atual["Email"]
        variables["email_cliente"] = email_cliente
        
        # Preencher campo nome
        campo_nome = driver.find_element(By.ID, "campo_nome")
        campo_nome.send_keys(nome_cliente)
        
        # Clicar botão
        botao = driver.find_element(By.ID, "btn_abrir_popup")
        botao.click()
        
        # Aguardar popup
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "popup_email"))
        )
        
        # Preencher email no popup
        campo_email = driver.find_element(By.ID, "campo_email_popup")
        campo_email.send_keys(email_cliente)
        
        # Salvar
        btn_salvar = driver.find_element(By.ID, "btn_salvar_popup")
        btn_salvar.click()
        
        # Pausa
        time.sleep(2)  # Aguardar processamento

finally:
    driver.quit()
```

## 💡 Dicas e Boas Práticas

### 📊 Planilhas
- Use nomes de colunas sem espaços ou caracteres especiais
- Sempre defina um nome de variável descritivo para a planilha
- Teste com poucas linhas primeiro

### 🔄 Loops
- Sempre defina um máximo de iterações para evitar loops infinitos
- Use nomes descritivos para a variável da linha atual
- Adicione pausas entre iterações para não sobrecarregar o site

### 🔢 Variáveis
- Use nomes descritivos: `nome_cliente` em vez de `var1`
- Teste a obtenção de células com dados reais
- Verifique se os nomes das colunas estão corretos

### 🌐 Selenium com Variáveis
- Use `${variavel}` em qualquer campo de texto
- Teste seletores dinâmicos com cuidado
- Adicione esperas após usar variáveis em campos

## 🚨 Tratamento de Erros

### Problemas Comuns:
1. **Planilha não encontrada**: Verifique o caminho do arquivo
2. **Coluna não existe**: Confira os nomes das colunas na planilha
3. **Loop infinito**: Sempre defina máximo de iterações
4. **Elemento não encontrado**: Use aguardar elemento antes de interagir

### Soluções:
- Sempre teste com dados pequenos primeiro
- Use pausas entre ações
- Verifique logs de execução para identificar problemas
- Mantenha backups das planilhas originais

## 🎯 Casos de Uso Avançados

### 1. Filtrar Dados da Planilha
```python
# Processar apenas clientes ativos
df_filtrado = df_clientes[df_clientes['Status'] == 'Ativo']
```

### 2. Atualizar Planilha com Resultados
```python
# Adicionar coluna de status após processamento
df_clientes['Processado'] = 'Sim'
df_clientes.to_excel('clientes_processados.xlsx', index=False)
```

### 3. Múltiplas Planilhas
```python
# Carregar dados de diferentes fontes
df_clientes = pd.read_excel('clientes.xlsx')
df_produtos = pd.read_excel('produtos.xlsx')
```

## 🔄 Próximos Passos

Com esses blocos, você pode criar automações complexas que:
- Processam centenas de registros automaticamente
- Integram dados de planilhas com sites web
- Geram relatórios de processamento
- Tratam erros e continuam o processamento

Experimente começar com uma planilha pequena (5-10 linhas) para testar seu workflow antes de processar dados grandes!