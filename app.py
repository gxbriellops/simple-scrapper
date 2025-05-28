import os
from dotenv import load_dotenv
from typing import Iterator
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document as LCDocument
from docling.document_converter import DocumentConverter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from typing import Iterable
import glob
from langchain_community.vectorstores import FAISS


load_dotenv()

gemini_api = os.getenv('GEMINI_API')

class DoclingPDFLoader(BaseLoader):

    def __init__(self, file_path: str | list[str]) -> None:
        self._file_paths = file_path if isinstance(file_path, list) else [file_path]
        self._converter = DocumentConverter()

    def lazy_load(self) -> Iterator[LCDocument]:
        for source in self._file_paths:
            dl_doc = self._converter.convert(source).document
            text = dl_doc.export_to_markdown()
            yield LCDocument(page_content=text)

# Caminho do diretório com os arquivos
file_dir = r"C:\Users\Gabriel Lopes\Documents\PROJETOS_PROGRAMAÇÃO_2\create-markdown\langChain_docs"

# Lista todos os arquivos .md (ou troque para o tipo desejado)
file_list = glob.glob(os.path.join(file_dir, "*.md"))

loader = DoclingPDFLoader(file_path=file_list)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

docs = loader.load()

splits = text_splitter.split_documents(docs)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=gemini_api
)

vectorstore = FAISS.from_documents(
    splits,
    embeddings
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

rag_chain.invoke(input=question)