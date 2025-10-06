# 📄 Web Scraper - Sistema de Documentação Automatizada

Sistema avançado de web scraping com interface gráfica para extração e conversão de conteúdo web em documentação estruturada em Markdown.

## 📋 Descrição

Este projeto oferece uma solução completa para extração de conteúdo de sites e conversão automática para arquivos Markdown bem formatados. Ideal para criar documentação local de APIs, tutoriais, artigos técnicos e outros recursos web.

### Características Principais

- **Interface Gráfica Intuitiva**: Aplicação desktop desenvolvida em Tkinter
- **Conversão Inteligente**: Utiliza Docling para conversão precisa de HTML para Markdown
- **Processamento em Lote**: Suporte para múltiplas URLs simultaneamente
- **Organização Automática**: Geração de índices e estruturação hierárquica de arquivos
- **Arquitetura SOLID**: Código modular, testável e extensível
- **Gestão de Dependências**: Sistema de injeção de dependências para fácil manutenção

## 🏗️ Arquitetura

O projeto foi desenvolvido seguindo os princípios SOLID de design orientado a objetos:

- **Single Responsibility**: Cada classe possui uma única responsabilidade bem definida
- **Open/Closed**: Extensível através de interfaces sem modificação de código existente
- **Liskov Substitution**: Implementações podem ser substituídas sem quebrar funcionalidades
- **Interface Segregation**: Interfaces específicas e enxutas
- **Dependency Inversion**: Dependência de abstrações, não de implementações concretas

Para mais detalhes sobre a arquitetura, consulte [SOLID_PRINCIPLES.md](SOLID_PRINCIPLES.md).

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Dependências

Instale as dependências necessárias utilizando:

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` contém:
- **beautifulsoup4**: Parser HTML/XML
- **docling**: Conversor de documentos para Markdown
- **requests**: Biblioteca HTTP

## 🚀 Execução

### Modo Interface Gráfica (Recomendado)

Execute a aplicação através da interface gráfica:

```bash
python interface.py
```

**Nota sobre Execução**: O projeto foi desenvolvido para ser executado via script Python `.py` diretamente, não como executável compilado. Isso permite maior flexibilidade e evita dependências de drivers externos (como webdriver para Selenium). Para facilitar o acesso, é recomendado criar atalhos que abram o terminal no diretório do projeto.

### Configuração via Interface

1. **URLs**: Insira uma ou mais URLs dos sites a documentar
2. **Nome da Pasta**: Defina o nome da pasta de destino em `DOCUMENTAÇÃO/`
3. **Limite de Páginas**: Configure o número máximo de páginas a processar (1-1000)
4. **Selenium**: Opção desabilitada por padrão (requer configuração adicional)

### Modo Programático

Para integração em scripts ou automações:

```python
from scrapper import SimpleWebScraper

# Configuração básica
scraper = SimpleWebScraper(
    urls="https://exemplo.com.br",
    max_pages=50
)

# Executar scraping
scraper.run()
```

### Modo Avançado com Injeção de Dependências

```python
from scrapper import SimpleWebScraper, DoclingConverter

# Usar conversor customizado
custom_converter = DoclingConverter()
scraper = SimpleWebScraper(
    urls=["https://site1.com", "https://site2.com"],
    converter=custom_converter,
    max_pages=100
)

scraper.run()
```

## 📁 Estrutura de Saída

```
DOCUMENTAÇÃO/
└── nome_da_pasta/
    ├── index.md                    # Índice geral com todas as páginas
    ├── pagina_inicial.md           # Conteúdo convertido
    ├── documentacao_api.md
    ├── tutorial_01.md
    └── ...
```

### Formato dos Arquivos Gerados

Cada arquivo Markdown contém:

```markdown
# Título da Página

**Fonte:** https://exemplo.com.br/pagina
**Data:** 2025-10-06 14:30:00

================================================================================

[Conteúdo extraído e convertido para Markdown]
```

### Arquivo de Índice

O `index.md` gerado automaticamente contém:

- Data e hora da extração
- Lista de URLs de origem
- Total de páginas processadas
- Links para todos os arquivos gerados

## 🔧 Personalização

### Criar Conversor Customizado

```python
from scrapper import IContentConverter

class MeuConverter(IContentConverter):
    def convert(self, url: str) -> str:
        # Implementação personalizada
        return conteudo_markdown

# Usar conversor customizado
scraper = SimpleWebScraper(
    urls="https://exemplo.com",
    converter=MeuConverter()
)
```

### Modificar Diretório de Saída

```python
scraper = SimpleWebScraper(urls="https://exemplo.com")
scraper.output_dir = "DOCS/minha_pasta"
scraper.run()
```

## 📂 Estrutura do Projeto

```
simple-scrapper/
├── interface.py              # Interface gráfica (Tkinter)
├── scrapper.py              # Lógica principal de scraping
├── requirements.txt         # Dependências do projeto
├── LICENSE                  # Licença MIT
├── README.md               # Este arquivo
├── SOLID_PRINCIPLES.md     # Documentação da arquitetura
└── DOCUMENTAÇÃO/           # Pasta de saída (gerada automaticamente)
```

## 🎯 Componentes Principais

### `interface.py`

- **InputValidator**: Validação de entradas do usuário
- **FolderManager**: Gerenciamento de pastas e diretórios
- **URLFieldManager**: Controle dinâmico de campos de URL
- **WebScraperGUI**: Interface gráfica principal

### `scrapper.py`

- **IContentConverter**: Interface para conversores de conteúdo
- **DoclingConverter**: Implementação usando biblioteca Docling
- **FileManager**: Gerenciamento de arquivos e nomenclatura
- **IndexGenerator**: Geração de índices
- **URLProcessor**: Processamento individual de URLs
- **SimpleWebScraper**: Orquestrador principal

## ⚙️ Configurações

### Limites e Controles

- **max_pages**: Controla quantas páginas serão processadas (padrão: 100)
- **output_dir**: Define o diretório de saída (padrão: nome baseado no domínio)
- **use_selenium**: Flag para habilitar Selenium (requer configuração adicional)

### Tratamento de Erros

O sistema possui tratamento robusto de erros:
- Fallback automático em caso de falha de conversão
- Logs detalhados de todas as operações
- Continuação do processamento mesmo com falhas individuais

## 🐛 Troubleshooting

### Erro: "Nenhum conteúdo foi extraído"

**Causa**: O site pode estar bloqueando requisições ou usando JavaScript pesado.

**Solução**: 
- Verifique se a URL está acessível no navegador
- Alguns sites requerem Selenium (requer configuração adicional de webdriver)

### Erro: "Módulo não encontrado"

**Causa**: Dependências não instaladas corretamente.

**Solução**:
```bash
pip install -r requirements.txt
```

### Interface não abre

**Causa**: Tkinter não está instalado ou configurado.

**Solução** (Ubuntu/Debian):
```bash
sudo apt-get install python3-tk
```

### Muitas dependências no ambiente

**Causa**: Ambiente Python com muitos pacotes instalados.

**Solução**: Use ambiente virtual ou limpe dependências:
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar apenas dependências necessárias
pip install -r requirements.txt
```

## 📊 Performance

- **Velocidade**: ~2-5 páginas por segundo (depende da conexão e site)
- **Uso de Memória**: ~50-150 MB durante operação
- **Armazenamento**: Variável conforme tamanho das páginas

## 🔐 Considerações de Uso

### Uso Ético

- Respeite os termos de serviço dos sites
- Verifique o arquivo `robots.txt` do site
- Utilize delays apropriados entre requisições
- Não sobrecarregue servidores com requisições excessivas

### Limitações

- Não processa conteúdo protegido por autenticação
- Sites com JavaScript pesado podem requerer Selenium (configuração adicional)
- Alguns sites implementam proteção contra scraping

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

### Diretrizes

- Siga os princípios SOLID já implementados
- Adicione testes para novas funcionalidades
- Mantenha a documentação atualizada
- Utilize type hints em Python

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

```
MIT License - Copyright (c) 2025 Gabriel Lopes
```

## 👤 Autor

**Gabriel Lopes**

## 🙏 Agradecimentos

- **Docling**: Excelente biblioteca para conversão de documentos
- **BeautifulSoup**: Parser HTML robusto e confiável
- **Comunidade Python**: Pelo ecossistema rico de bibliotecas

## 📮 Suporte

Para reportar bugs ou solicitar features, abra uma issue no repositório do projeto.

---

**Desenvolvido com Python 🐍 | Interface com Tkinter | Conversão com Docling**
