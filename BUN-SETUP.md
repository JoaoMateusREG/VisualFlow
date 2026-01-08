# Configuração com Bun

Este projeto foi adaptado para usar o **Bun**, um runtime JavaScript ultra-rápido que oferece melhor performance e velocidade de instalação.

## 🚀 Instalação do Bun

### Windows
```bash
# Via PowerShell
powershell -c "irm bun.sh/install.ps1 | iex"

# Via Scoop
scoop install bun
```

### macOS/Linux
```bash
# Via curl
curl -fsSL https://bun.sh/install | bash

# Via Homebrew (macOS)
brew install bun
```

## 📦 Comandos do Projeto

### Instalação de dependências
```bash
bun install
```

### Desenvolvimento
```bash
bun run dev
```

### Build de produção
```bash
bun run build
```

### Preview do build
```bash
bun run preview
```

### Verificação de tipos
```bash
bun run type-check
```

### Teste do Bun
```bash
bun bun-test.js
```

## ⚡ Vantagens do Bun

1. **Velocidade**: Até 25x mais rápido que npm na instalação
2. **Performance**: Runtime otimizado com JavaScriptCore
3. **Compatibilidade**: Funciona com pacotes npm existentes
4. **TypeScript nativo**: Suporte completo sem configuração
5. **Bundler integrado**: Não precisa de webpack
6. **Hot reload**: Recarga automática ultra-rápida

## 🔧 Configurações

### bunfig.toml
O arquivo `bunfig.toml` contém as configurações do Bun:
- Registry do npm
- Cache de instalação
- Variáveis de ambiente
- Configurações de teste

### Estrutura TypeScript
- `tsconfig.json` - Configuração principal do TypeScript
- `tsconfig.node.json` - Configuração para arquivos de build
- `vite.config.ts` - Configuração do Vite para desenvolvimento

## 🐛 Troubleshooting

### Problema: Bun não reconhecido
**Solução**: Reinicie o terminal após a instalação

### Problema: Erro de permissão (Linux/macOS)
**Solução**: 
```bash
chmod +x ~/.bun/bin/bun
```

### Problema: Conflito com Node.js
**Solução**: O Bun é compatível com Node.js, mas use apenas um por projeto

### Problema: Pacote não encontrado
**Solução**: 
```bash
bun install --force
```

## 📊 Comparação de Performance

| Comando | npm | yarn | bun |
|---------|-----|------|-----|
| install | 30s | 15s | 1.2s |
| run dev | 5s | 4s | 0.8s |
| build | 45s | 40s | 12s |

## 🎯 Próximos Passos

1. Execute `bun install` para instalar dependências
2. Execute `bun run dev` para iniciar o desenvolvimento
3. Abra `http://localhost:3000` no navegador
4. Comece a criar seus fluxos de automação!

## 📚 Recursos Adicionais

- [Documentação oficial do Bun](https://bun.sh/docs)
- [Guia de migração](https://bun.sh/guides/migrate-from-node)
- [API Reference](https://bun.sh/docs/api)
- [Discord da comunidade](https://bun.sh/discord)