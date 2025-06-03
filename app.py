import os
from dotenv import load_dotenv
from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import Iterable
import glob
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader

load_dotenv()

gemini_api = os.getenv('GEMINI_API')

# Caminho do diretório com os arquivos
file_dir = r"C:\Users\Gabriel Lopes\Documents\PROJETOS_PROGRAMAÇÃO_2\create-markdown\docs.streamlit.io"

# Lista todos os arquivos .md (ou troque para o tipo desejado)
file_list = glob.glob(os.path.join(file_dir, "*.md"))

loader = DirectoryLoader(path=file_dir,
                         glob="*.md",
                         loader_cls=UnstructuredMarkdownLoader)

docs = loader.load()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=gemini_api
)

vectorstore = FAISS.from_documents(
    docs,
    embeddings,
    
)

llm = GoogleGenerativeAI(
    model = 'gemini-2.0-flash',
    google_api_key = gemini_api,
    temperature = 0.5
)

def format_docs(docs: Iterable[LCDocument]):
    return "\n\n".join(doc.page_content for doc in docs)

retriever = vectorstore.as_retriever()

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

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

question = input('Sua pergunta: ')

resposta = rag_chain.invoke(input=question)

print(resposta)