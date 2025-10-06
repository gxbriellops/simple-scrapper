# 🚀 Web Scraper Avançado

Sistema avançado de scraping web com interface gráfica para extração e documentação de sites.

## ✨ Funcionalidades

### 🎯 Principais Recursos

- **Scrapy + Selenium**: Combinação poderosa para sites estáticos e dinâmicos
- **Interface Gráfica**: Fácil de usar com tkinter moderno
- **Multi-método de Extração**:
  - Selenium para conteúdo JavaScript/dinâmico
  - Scrapy para crawling eficiente
  - Docling para conversão em Markdown
  - BeautifulSoup como fallback
- **Sistema Inteligente de Cache**: Evita reprocessar URLs já visitadas
- **Tratamento Robusto de Erros**: Retry automático e fallbacks múltiplos
- **Controle de Profundidade**: Limite configurável de páginas
- **Filtros Inteligentes**: Ignora automaticamente arquivos binários e páginas irrelevantes

### 📊 Recursos Avançados

- ✅ **Requisições Assíncronas**: Até 8 requisições simultâneas
- ✅ **Deduplicação**: URLs processadas apenas uma vez
- ✅ **Metadados Persistentes**: Salva progresso entre execuções
- ✅ **Índice Automático**: Gera INDEX.md com todos os arquivos
- ✅ **Logs Detalhados**: Acompanhamento em tempo real
- ✅ **Respeito ao robots.txt**: Crawling ético
- ✅ **User Agent Moderno**: Evita bloqueios

## 📦 Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Instalar ChromeDriver

O Selenium requer o ChromeDriver. Baixe em: https://chromedriver.chromium.org/

Ou use webdriver-manager (já incluído em requirements.txt):
```python
from webdriver_manager.chrome import ChromeDriverManager
```

## 🎮 Uso

### Interface Gráfica

```bash
python interface.py
```

**Campos da Interface:**

1. **URL do Site**: URL completa do site a ser raspado
2. **Nome da Pasta**: Nome da pasta dentro de `DOCUMENTAÇÃO/`
3. **Limite de Páginas**: Máximo de páginas a processar (1-1000)
4. **Usar Selenium**: ☑️ para sites com JavaScript

### Modo Programático

```python
from scrapper import SimpleWebScraper

# Criar scraper
scraper = SimpleWebScraper(
    url="https://exemplo.com",
    use_selenium=True,  # Usar Selenium para conteúdo dinâmico
    max_pages=100       # Limitar a 100 páginas
)

# Executar
scraper.run()
```

## 📁 Estrutura de Saída

```
DOCUMENTAÇÃO/
└── nome_da_pasta/
    ├── INDEX.md              # Índice geral
    ├── .metadata.json        # Metadados (cache)
    ├── pagina_1.md
    ├── pagina_2.md
    └── ...
```

### Formato dos Arquivos

Cada arquivo `.md` contém:

```markdown
# Título da Página

**Fonte:** https://exemplo.com/pagina
**Data:** 2025-10-05 14:30:00

================================================================================

[Conteúdo extraído em Markdown]
```

## ⚙️ Configurações

### scrapper.py (linhas 28-42)

```python
custom_settings = {
    'ROBOTSTXT_OBEY': True,           # Respeitar robots.txt
    'CONCURRENT_REQUESTS': 8,         # Requisições simultâneas
    'DOWNLOAD_DELAY': 1,              # Delay entre requisições (seg)
    'RETRY_TIMES': 5,                 # Tentativas em caso de erro
    'DEPTH_LIMIT': 5,                 # Profundidade máxima
    'DOWNLOAD_TIMEOUT': 30,           # Timeout de download (seg)
}
```

### Filtros de URL (linhas 77-87)

URLs ignoradas automaticamente:
- `/tag/`, `/category/`, `/search`
- `/login`, `/register`, `/cart`
- Paginação (`?page=`)
- Âncoras (`#`)

### Extensões Ignoradas (linhas 70-76)

- Imagens: png, jpg, jpeg, gif, svg, ico
- Documentos: pdf, zip, rar, tar, gz
- Executáveis: exe, dmg, pkg, deb, rpm
- Mídia: mp4, avi, mov, mp3, wav
- Assets: css, js, woff, ttf

## 🔧 Personalização

### Adicionar Filtros Customizados

```python
# Em scrapper.py, linha 77
deny=[
    r'/tag/',
    r'/category/',
    r'/seu-filtro-aqui/',  # Adicione aqui
]
```

### Modificar Selenium Options

```python
# Em scrapper.py, linha 105-121
chrome_options.add_argument('--seu-argumento')
```

### Ajustar Extração de Conteúdo

```python
# Em scrapper.py, linha 229-230
# Modificar quais elementos remover
for element in soup(['script', 'style', 'nav', 'footer']):
    element.decompose()
```

## 🐛 Solução de Problemas

### Selenium não funciona

1. Verifique se o ChromeDriver está instalado
2. Verifique a versão do Chrome vs ChromeDriver
3. O scraper continuará funcionando sem Selenium (apenas Scrapy)

### Timeout/Erro de Conexão

- Aumente `DOWNLOAD_TIMEOUT` em `custom_settings`
- Reduza `CONCURRENT_REQUESTS`
- Aumente `DOWNLOAD_DELAY`

### Páginas vazias

- Ative o Selenium para sites com JavaScript
- Verifique se o site não bloqueia bots
- Ajuste o User Agent

### Muitas páginas ignoradas

- Revise os filtros em `deny=[]`
- Verifique `DEPTH_LIMIT`
- Aumente `max_pages`

## 📊 Estatísticas de Performance

- **Velocidade**: ~8 páginas/segundo (sem Selenium)
- **Velocidade c/ Selenium**: ~1-2 páginas/segundo
- **Uso de Memória**: ~100-200 MB
- **CPU**: Moderado (multi-thread)

## 📝 Logs e Debugging

### Ativar Logs Detalhados

```python
# Em scrapper.py, linha 35
'LOG_LEVEL': 'INFO',  # ou 'DEBUG'
```

### Arquivo de Metadados

O arquivo `.metadata.json` contém:
- URLs processadas (cache)
- Data da última execução
- URLs com erro
- Total de páginas

## 🤝 Contribuindo

Sugestões e melhorias são bem-vindas!

## ⚠️ Avisos Legais

- Respeite os termos de serviço dos sites
- Respeite robots.txt (ativado por padrão)
- Use delays apropriados entre requisições
- Não sobrecarregue servidores

## 📄 Licença

MIT License - use livremente!

---

**Desenvolvido com ❤️ usando Scrapy, Selenium, Docling e Tkinter**
