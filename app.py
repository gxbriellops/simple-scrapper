import os
from dotenv import load_dotenv
from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import Iterable
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import ChatOpenAI

# Carregar variáveis de ambiente
load_dotenv()

deepseek_api = os.getenv('DEEPSEEK_API')

# Caminho do diretório com os arquivos
file_dir = r"C:\Users\Gabriel Lopes\Documents\PROJETOS_PROGRAMAÇÃO_2\create-markdown\docs.streamlit.io"

loader = DirectoryLoader(
    path=file_dir,
    glob="*.md",
    loader_cls=TextLoader,
    loader_kwargs={'encoding': 'utf-8'}  # Importante para caracteres especiais
)

# Configurar o text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

# Carregar e dividir documentos
docs = loader.load()
splits = text_splitter.split_documents(docs)

# Configurar embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Criar vectorstore
vectorstore = Chroma.from_documents(
    splits,
    embeddings
)

llm = ChatOpenAI(
    model='deepseek/deepseek-chat-v3-0324:free',
    temperature=0.5,
    base_url='https://openrouter.ai/api/v1'
)

def format_docs(docs: Iterable[LCDocument]):
    return "\n\n".join(doc.page_content for doc in docs)

# Configurar retriever
retriever = vectorstore.as_retriever()

# Template do prompt
prompt = PromptTemplate.from_template(
    """Você é um assistente especializado em programação. 
Responda dúvidas sobre bibliotecas, explique conceitos de forma clara e forneça exemplos de código práticos e comentados sempre que possível.

Contexto relevante extraído da documentação:
{context}

Pergunta do usuário:
{question}

Responda de forma objetiva, didática e, se aplicável, inclua exemplos de código em Python.
"""
)

# Criar a chain RAG
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# CORREÇÃO 3: Capturar e exibir o resultado
question = input('Sua pergunta: ')
result = rag_chain.invoke(question)  # Passar diretamente a string
print(result)