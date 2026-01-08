# Integração com Selenium

Esta aplicação foi especialmente adaptada para gerar código Selenium automaticamente baseado nos fluxos visuais criados.

## 🎯 Funcionalidades Implementadas

### 1. **Navegação/Login** 🔐
- **URL de destino**: Página para navegar
- **Campos de login**: Usuário e senha com seletores configuráveis
- **Tipos de seletor**: ID, Name, XPath, CSS Selector, etc.
- **Timeout configurável**: Tempo de espera para elementos

**Código gerado:**
```python
driver.get("https://exemplo.com")
username_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "usuario"))
)
username_field.send_keys("meu_usuario")
```

### 2. **Clicar Elemento** 🖱️
- **Seletores Selenium**: Todos os tipos suportados (ID, XPath, CSS, etc.)
- **Condições de espera**: Elemento presente, visível, clicável
- **Opções avançadas**: Scroll automático, duplo clique
- **Pausa configurável**: Tempo de espera após o clique

**Código gerado:**
```python
element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@id='submit']"))
)
element.click()
```

### 3. **Inserir Texto/Dados** ✍️
- **Campo de destino**: Seletor do input/textarea
- **Texto dinâmico**: Suporte a variáveis como ${cpf}
- **Opções**: Limpar campo antes, pressionar Enter
- **Validação**: Aguardar elemento estar disponível

**Código gerado:**
```python
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "nu_cns"))
)
element.clear()
element.send_keys("12345678901")
```

### 4. **Aguardar Elemento** ⏱️
- **Tipos de espera**: Tempo fixo, aguardar elemento, condição específica
- **Condições avançadas**: Visibilidade, texto presente, elemento selecionado
- **Retry automático**: Tentativas configuráveis
- **Timeout flexível**: Tempo máximo de espera

**Código gerado:**
```python
WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "resultado"))
)
```

## 🔧 Tipos de Seletores Suportados

| Tipo | Selenium | Exemplo |
|------|----------|---------|
| **ID** | `By.ID` | `usuario` |
| **Name** | `By.NAME` | `btn_pesquisar` |
| **Class Name** | `By.CLASS_NAME` | `form-control` |
| **Tag Name** | `By.TAG_NAME` | `button` |
| **XPath** | `By.XPATH` | `//input[@name='cpf']` |
| **CSS Selector** | `By.CSS_SELECTOR` | `#login .btn-primary` |
| **Link Text** | `By.LINK_TEXT` | `Clique aqui` |
| **Partial Link** | `By.PARTIAL_LINK_TEXT` | `Clique` |

## ⏳ Condições de Espera

| Condição | Descrição | Uso |
|----------|-----------|-----|
| `presence_of_element_located` | Elemento presente no DOM | Verificar se existe |
| `visibility_of_element_located` | Elemento visível na tela | Aguardar aparecer |
| `element_to_be_clickable` | Elemento clicável | Antes de clicar |
| `invisibility_of_element_located` | Elemento invisível | Aguardar sumir |
| `text_to_be_present_in_element` | Texto presente | Validar conteúdo |
| `element_to_be_selected` | Elemento selecionado | Checkboxes/radios |

## 🚀 Como Usar

### 1. **Criar o Fluxo**
1. Arraste blocos da sidebar esquerda para o canvas
2. Conecte os blocos na ordem desejada
3. Clique em cada bloco para configurar na sidebar direita

### 2. **Configurar Blocos**
1. **Selecione o tipo de seletor** (ID, XPath, etc.)
2. **Digite o valor do seletor** (ex: `btn_pesquisar`)
3. **Configure timeouts e condições**
4. **Veja o código Selenium gerado em tempo real**

### 3. **Executar e Exportar**
1. Clique em **"Executar Fluxo"** para validar
2. Veja o código Python completo no console
3. Use **"Salvar"** para exportar o fluxo
4. Copie o código gerado para seu projeto

## 📝 Exemplo Prático

Baseado no seu código original, aqui está um fluxo típico:

### Fluxo: Login + Busca + Extração
1. **Navegação/Login**
   - URL: `https://sisregiii.saude.gov.br/`
   - Usuário: Campo `usuario` (ID)
   - Senha: Campo `senha` (ID)
   - Botão: XPath do botão de login

2. **Aguardar Elemento**
   - Aguardar campo de busca aparecer
   - Seletor: `nu_cns` (Name)
   - Condição: Elemento visível

3. **Inserir Texto**
   - Campo: `nu_cns` (Name)
   - Texto: `${cpf}` (variável)
   - Limpar antes: ✅

4. **Clicar Elemento**
   - Botão: `btn_pesquisar` (Name)
   - Condição: Elemento clicável
   - Pausa após: 2s

5. **Aguardar Elemento**
   - Resultado: XPath da data de nascimento
   - Timeout: 30s
   - Retry: 3 tentativas

## 🎨 Interface

### Sidebar Esquerda
- **Blocos disponíveis** para arrastar
- **Instruções de uso**
- **Ícones intuitivos** para cada tipo

### Canvas Central
- **Área de trabalho** para criar fluxos
- **Conexões visuais** entre blocos
- **Zoom e navegação** completos

### Sidebar Direita
- **Configurações detalhadas** do bloco selecionado
- **Preview do código Selenium** em tempo real
- **Dicas e exemplos** contextuais
- **Validação de campos** automática

## 🔍 Dicas Avançadas

### XPath Otimizado
```xpath
// Seu exemplo original otimizado
//td/b[contains(text(), 'Data de Nascimento')]/ancestor::tr[1]/following-sibling::tr[1]/td[1]
```

### Tratamento de Erros
O código gerado inclui:
- **Try/catch** automático
- **Timeouts configuráveis**
- **Retry em falhas**
- **Cleanup do driver**

### Variáveis Dinâmicas
Use `${variavel}` nos campos de texto para:
- `${cpf}` - CPF da planilha
- `${nome}` - Nome do usuário
- `${data}` - Data formatada

## 📊 Código Completo Gerado

O sistema gera código Python completo incluindo:
- Imports necessários
- Inicialização do driver
- Todos os passos do fluxo
- Tratamento de erros
- Cleanup final

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# ... outros imports

driver = webdriver.Chrome()
try:
    # Seus passos aqui...
finally:
    driver.quit()
```

Esta integração torna a criação de automações Selenium muito mais visual e intuitiva!