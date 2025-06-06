# 🏛️ Athena Code - AI RAG Assistant

> **Assistente de IA especializado em documentação técnica com capacidades de web scraping e consulta inteligente**

## 📖 Sobre o Projeto

O **Athena Code** é uma aplicação que combina web scraping inteligente com um sistema de RAG (Retrieval-Augmented Generation) para criar um assistente de IA especializado em documentação técnica. O projeto permite extrair conteúdo de websites de documentação, converter para formato Markdown e depois consultá-los através de uma interface de chat alimentada pela IA do Google Gemini.

### 🎯 Funcionalidades Principais

**Web Scraping Inteligente:**
- Extração automática de conteúdo de websites de documentação
- Conversão para formato Markdown preservando a estrutura
- Processamento de múltiplas páginas do mesmo domínio
- Geração automática de índices organizados

**Sistema RAG Avançado:**
- Carregamento e indexação de documentos Markdown
- Busca semântica usando embeddings do Google Gemini
- Respostas baseadas exclusivamente na documentação carregada
- Interface de chat intuitiva e responsiva

**Interface Streamlit:**
- Design limpo e profissional
- Configuração fácil via sidebar
- Chat em tempo real com streaming de respostas
- Gerenciamento de sessões e histórico

## 🚀 Inspiração e Motivação

Este projeto foi inspirado em uma das demonstrações que vi no anúncio da **Asimov Academy**, onde percebi o potencial de combinar web scraping com sistemas de IA para criar assistentes especializados. Decidi desenvolver minha própria versão de forma completamente autodidata, explorando tecnologias como Langchain, FAISS e Google Gemini AI para criar uma solução robusta e prática.

## ⚠️ Requisitos Importantes

### Versão do Python
**IMPORTANTE:** Use Python 3.11.x (recomendado: 3.11.11) ou anterior. **NÃO use Python 3.12+**

O projeto utiliza a biblioteca `docling` que depende do TensorFlow, e há conflitos conhecidos com Python 3.12. Durante o desenvolvimento, utilizei especificamente a versão 3.11.11 sem problemas.

### API do Google Gemini
Você precisará de uma chave da API do Google Gemini. Obtenha gratuitamente em [Google AI Studio](https://aistudio.google.com/).

## 🛠️ Instalação e Configuração

### Passo 1: Preparação do Ambiente

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/athena-code.git
cd athena-code

# Verifique sua versão do Python (deve ser 3.11.x)
python --version

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### Passo 2: Instalação das Dependências

```bash
# Instale as dependências
pip install -r requirements.txt
```

**Nota:** A instalação pode demorar alguns minutos devido às dependências do TensorFlow e outras bibliotecas de machine learning.

### Passo 3: Configuração da API

1. Obtenha sua chave da API do Google Gemini
2. Crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API="sua_chave_api_aqui"
```

### Passo 4: Execução

```bash
# Execute a aplicação
streamlit run app.py
```

A aplicação abrirá automaticamente em `http://localhost:8501`

## 📚 Como Usar

### 1. Web Scraping de Documentação

Na sidebar da aplicação:

1. **Insira a URL** da documentação que deseja extrair (ex: `https://docs.streamlit.io`)
2. **Clique em "Extrair Conteúdo"** e aguarde o processamento
3. O sistema irá:
   - Descobrir todos os links relacionados no mesmo domínio
   - Extrair o conteúdo de cada página
   - Converter tudo para formato Markdown
   - Organizar os arquivos em um diretório específico

### 2. Carregamento de Documentos

1. **Selecione o diretório** com os documentos Markdown na sidebar
2. **Clique em "Carregar Documentos"** para indexar o conteúdo
3. O sistema criará embeddings e preparará o sistema RAG

### 3. Consulta Inteligente

1. **Use o chat** na área principal para fazer perguntas sobre a documentação
2. **Faça perguntas específicas** como:
   - "Como criar um componente de slider no Streamlit?"
   - "Quais são os parâmetros da função st.plotly_chart?"
   - "Como implementar autenticação de usuários?"

## 🏗️ Arquitetura Técnica

### Componentes Principais

**SimpleWebScraper** (`main.py`):
- Utiliza `docling` para conversão de conteúdo web para Markdown
- Implementa descoberta automática de links relacionados
- Gera estrutura organizada de arquivos com índices

**Sistema RAG** (`app.py`):
- **Embeddings:** Google Gemini `models/embedding-001`
- **Vector Store:** FAISS para busca semântica eficiente
- **LLM:** Google Gemini `gemini-2.0-flash` para geração de respostas
- **Retrieval:** Top-5 documentos mais relevantes por consulta

**Interface Streamlit:**
- Design responsivo com sidebar para configurações
- Chat streaming para respostas em tempo real
- Gerenciamento de estado para sessões persistentes

### Fluxo de Dados

```
URL → Web Scraper → Markdown Files → FAISS Indexing → RAG System → Chat Interface
```

## 🎨 Personalização

### Modificando o Prompt do Sistema

No arquivo `app.py`, você pode personalizar o comportamento do assistente modificando o `PromptTemplate`:

```python
prompt = PromptTemplate.from_template(
    """Seu prompt personalizado aqui...
    
    {context}
    {question}
    """
)
```

### Ajustando Parâmetros de Busca

Modifique os parâmetros do retriever para alterar a qualidade das respostas:

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Número de documentos recuperados
)
```

## 🔧 Solução de Problemas

### Erro de Compatibilidade do TensorFlow
```
Solução: Use Python 3.11.x em vez de 3.12+
```

### Erro de API do Gemini
```
Solução: Verifique se sua chave API está correta no arquivo .env
```

### Problemas de Memória
```
Solução: Reduza o número de documentos processados ou aumente a RAM disponível
```

### Erro no Web Scraping
```
Solução: Verifique se a URL é acessível e se o site permite scraping
```

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

- Reportar bugs através das Issues
- Sugerir novas funcionalidades
- Submeter Pull Requests com melhorias
- Compartilhar exemplos de uso interessantes

## 🎓 Aprendizado e Desenvolvimento

Este projeto representa minha jornada autodidata no desenvolvimento de sistemas de IA aplicada. Foi uma oportunidade incrível para explorar:

- **RAG Systems:** Compreensão profunda de como combinar recuperação de informações com geração de linguagem
- **Web Scraping Inteligente:** Uso de bibliotecas modernas como `docling` para extração robusta de conteúdo
- **Vector Databases:** Implementação prática com FAISS para busca semântica
- **LangChain Framework:** Orquestração de componentes de IA de forma elegante
- **Interface de Usuário:** Criação de experiências intuitivas com Streamlit

A inspiração inicial veio da Asimov Academy, mas o desenvolvimento foi completamente independente, representando um exercício valioso de aprendizado prático em IA e desenvolvimento de software.

---

**Desenvolvido com ❤️ por Gabriel Lopes**

*Se este projeto foi útil para você, considere deixar uma ⭐ no repositório!*
