# Manual do Usuário - VisualFlow

## O que é o VisualFlow?

VisualFlow é um **construtor visual de workflows** para automação web e processamento de dados. Crie workflows arrastando blocos para um canvas e conectando-os—sem necessidade de programação.

## Começando

### Com Docker (Recomendado)
```bash
docker-compose up --build
```
Acesse em: **http://localhost:8164**

### Configuração Manual
Veja [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) para configuração de desenvolvimento local.

---

## Criando um Workflow

1. **Arraste blocos** da barra lateral para o canvas
2. **Conecte blocos** arrastando de um ponto de conexão para outro
3. **Configure blocos** clicando neles (configurações aparecem à direita)
4. **Execute o workflow** usando o botão Play no cabeçalho

---

## Referência de Blocos

### 🌐 Automação Web

| Bloco | Descrição |
|-------|-----------|
| **Login** | Navega para URL e preenche formulário de login |
| **Abrir Site** | Navega para uma URL |
| **Clicar Botão** | Clica em um elemento |
| **Aguardar** | Aguarda elemento ou tempo |
| **Pausa** | Pausa execução por N segundos |
| **Capturar Tabela** | Extrai tabela HTML para DataFrame |
| **Executar Script** | Executa JavaScript customizado |
| **Extrair Texto** | Extrai texto usando regex |

### 📊 Processamento de Dados

| Bloco | Descrição |
|-------|-----------|
| **Planilha** | Ler/Criar/Salvar arquivos Excel/CSV |
| **Variável** | Definir, obter ou transformar variáveis |
| **Agrupar Dados** | Agrupar DataFrame por coluna |
| **Transformar Coluna** | Aplicar transformação em coluna |
| **Executar Python** | Executar código Python customizado |

### 🔄 Controle de Fluxo

| Bloco | Descrição |
|-------|-----------|
| **Loop For** | Iterar sobre intervalo ou linhas de DataFrame |
| **Loop While** | Loop enquanto condição for verdadeira |
| **Condição** | Ramificação if/else |
| **Agendamento** | Configurar agendamento de execução |

---

## Salvando e Carregando Workflows

### Salvar Workflow
1. Clique no botão **Salvar** no cabeçalho
2. Digite um nome e descrição opcional
3. Workflow é salvo em `visualflow_data/workflows/`

### Carregar Workflow
1. Clique na aba **Workflows** na barra lateral
2. Selecione um workflow da lista
3. Clique em **Carregar**

### Importar Workflow (Arrastar e Soltar)
- Arraste um arquivo `.json` de workflow para o canvas
- Ou arraste para o modal de Workflows

---

## Persistência de Arquivos

Todos os arquivos criados pelos workflows são salvos em:

| Ambiente | Localização |
|----------|-------------|
| Docker | `/app/data` (mapeado para `./visualflow_data`) |
| Dev local | `./visualflow_data` (raiz do projeto) |

Isso inclui:
- Arquivos baixados pelo Selenium
- Planilhas criadas/salvas
- Tabelas capturadas

---

## Dicas

- **Use XPath** para seleção complexa de elementos
- **Teste seletores** no DevTools do navegador primeiro
- **Configure timeouts** apropriadamente para páginas lentas
- **Use variáveis** para passar dados entre blocos
- **Salve frequentemente** para evitar perder trabalho

---

## Solução de Problemas

Veja [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para problemas comuns e soluções.
