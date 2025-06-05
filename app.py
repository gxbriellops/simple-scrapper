import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '1'
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
import streamlit as st
import os
import glob
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredMarkdownLoader
from main import SimpleWebScraper
from langchain_core.output_parsers import StrOutputParser

# Configuração da página
st.set_page_config(page_title="Athena Code", page_icon="🏛️", layout="wide")

# Carregar variáveis de ambiente
load_dotenv()

def get_documentation_dirs():
    """Encontra diretórios com arquivos .md na raiz do projeto"""
    current_dir = os.getcwd()
    doc_dirs = []
    
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)
        if os.path.isdir(item_path):
            md_files = glob.glob(os.path.join(item_path, "*.md"))
            if md_files:
                doc_dirs.append(item_path)
    
    return doc_dirs

def load_documents(docs_dir):
    """Carrega documentos .md do diretório especificado"""

    docs_dir = os.path.abspath(docs_dir)

    try:
        loader = DirectoryLoader(
            path=docs_dir,
            glob="*.md",
            loader_cls=UnstructuredMarkdownLoader
        )
        docs = loader.load()
        return docs
    except Exception as e:
        st.error(f"Erro ao carregar documentos: {e}")
        return []

def create_rag_chain(_docs):
    """Cria a cadeia RAG com os documentos carregados"""
    try:
        gemini_api = os.getenv('GEMINI_API')
        if not gemini_api:
            st.error("Chave da API Gemini não encontrada no .env")
            return None
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=gemini_api
        )
        
        vectorstore = FAISS.from_documents(_docs, embeddings)
        
        llm = GoogleGenerativeAI(
            model='gemini-2.0-flash',
            google_api_key=gemini_api,
            temperature=0.3
        )
        
        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        prompt = PromptTemplate.from_template(
                    """Você é um assistente de programação especializado que DEVE responder EXCLUSIVAMENTE baseado na documentação fornecida.

                        ## Documentação Carregada
                        {context}

                        ## Pergunta do Usuário
                        {question}

                        ## REGRAS IMPORTANTES - LEIA COM ATENÇÃO:
                        
                        1. **RESPONDA APENAS COM BASE NA DOCUMENTAÇÃO ACIMA**
                        2. **Se a informação não estiver na documentação, diga claramente: "Esta informação não está disponível na documentação carregada."**
                        3. **NÃO use conhecimento geral fora da documentação fornecida**
                        4. **Sempre referencie seções específicas da documentação quando possível**

                        ## Formato da Resposta:

                        **Baseado na documentação carregada:**

                        1. **Resposta Direta**: Responda usando APENAS as informações da documentação
                        2. **Exemplo da Documentação**: Use exemplos que estão na documentação
                        3. **Explicação**: Explique baseado no que está documentado
                        4. **Referência**: Mencione qual parte da documentação você usou

                        **Se não houver informação suficiente na documentação:**
                        - Informe claramente que a informação não está disponível
                        - Sugira que o usuário verifique se carregou a documentação correta
                        - NÃO invente ou use conhecimento externo

                        **Lembre-se**: Você só conhece o que está na documentação fornecida acima. Tudo fora disso você deve dizer que não sabe.""")
        
        rag_chain = (
            {"context": retriever | (lambda docs: "\n\n".join(doc.page_content for doc in docs)), 
             "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return rag_chain
    except Exception as e:
        st.error(f"Erro ao criar RAG: {e}")
        return None

def main():
    st.title("🏛️ Athena Code, AI RAG Assistant")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Web Scraping
        st.subheader("🌐 Web Scraping")
        url = st.text_input("URL para extrair:", placeholder="https://docs.streamlit.io")
        
        if st.button("🚀 Extrair Conteúdo"):
            if url:
                with st.spinner("Extraindo..."):
                    try:
                        scraper = SimpleWebScraper(url)
                        scraper.run()
                        
                        # Contar documentos
                        md_files = glob.glob(os.path.join(scraper.output_dir, "*.md"))
                        doc_count = len([f for f in md_files if not f.endswith('index.md')])
                        
                        st.success(f"✅ {doc_count} documentos processados!")
                        st.session_state.last_scraping_dir = scraper.output_dir
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
        
        # Seleção de documentos
        st.subheader("📁 Documentos")
        
        # Buscar diretórios com documentação
        doc_dirs = get_documentation_dirs()
        
        if doc_dirs:
            # Adicionar último diretório de scraping se existir
            if hasattr(st.session_state, 'last_scraping_dir'):
                if st.session_state.last_scraping_dir not in doc_dirs:
                    doc_dirs.insert(0, st.session_state.last_scraping_dir)
            
            # Criar opções para o selectbox
            dir_options = {}
            for dir_path in doc_dirs:
                dir_name = os.path.basename(dir_path)
                file_count = len(glob.glob(os.path.join(dir_path, "*.md")))
                dir_options[f"{dir_name} ({file_count} arquivos)"] = dir_path
            
            selected_dir_label = st.selectbox(
                "Selecione o diretório:",
                options=list(dir_options.keys())
            )
            
        if st.button("📚 Carregar Documentos"):
            selected_dir = dir_options[selected_dir_label]
            
            # Garante que o caminho seja uma raw string
            if not selected_dir.startswith('r"'):
                # Se não começar com r", adiciona
                selected_dir = r"{}".format(selected_dir)
            
            # Remove qualquer prefixo 'r' duplicado se existir
            if selected_dir.startswith('r') and selected_dir.count('r"') > 1:
                selected_dir = selected_dir[1:]
            
            with st.spinner("Carregando..."):
                if os.path.isdir(selected_dir):
                    docs = load_documents(selected_dir)
                    if docs:
                        rag_chain = create_rag_chain(docs)
                        if rag_chain:
                            st.session_state.rag_chain = rag_chain
                            st.session_state.current_doc_dir = selected_dir
                            st.session_state.docs_loaded = True
                            doc_name = os.path.basename(selected_dir)
                            st.success(f"✅ {len(docs)} documentos de '{doc_name}' carregados!")
                else:
                    st.error(f"Diretório não encontrado: {selected_dir}")
    
    # Área principal - Chat
    st.header("💬 Chat")
    
    if not getattr(st.session_state, 'docs_loaded', False):
        st.info("👈 Carregue documentos para começar")
    else:
        # Inicializar histórico
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Mostrar mensagens
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Input do chat
        if prompt := st.chat_input("Faça sua pergunta..."):
            # Adicionar pergunta do usuário
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Gerar resposta
            with st.chat_message("assistant"):
                full_response = ""
                message_placeholder = st.empty()
                try:
                    for chunk in st.session_state.rag_chain.stream(prompt):
                        full_response += chunk
                        message_placeholder.write(full_response + "▌")
                    message_placeholder.write(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    error_msg = f"Erro: {e}"
                    st.error(error_msg)
    
    # Status na sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("📊 Status")
        
        if getattr(st.session_state, 'docs_loaded', False):
            st.success("✅ Pronto para chat")
        else:
            st.warning("⏳ Aguardando documentos")
        
        if st.button("🗑️ Limpar Chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()