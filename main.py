from docling.document_converter import DocumentConverter
import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urlparse, urljoin
from collections import defaultdict

url = 'https://pandas.pydata.org/docs/reference/index.html'
match = re.search(r'//([^/]+)\.(com|org|io|net|edu|gov|br|dev|ai)', url)
if match:
    output_dir = match.group(1)
else:
    output_dir = 'saida_padrao'

# Configurações de tamanho
MAX_FILE_SIZE_CHARS = 100000  # ~50k caracteres por arquivo
MAX_FILE_SIZE_MB = 2  # 1MB máximo por arquivo
MIN_FILE_SIZE_CHARS = 5000   # Tamanho mínimo antes de concatenar

# Criar o diretório se não existir
os.makedirs(output_dir, exist_ok=True)

def get_text_size_info(text):
    """Retorna informações sobre o tamanho do texto"""
    char_count = len(text)
    byte_count = len(text.encode('utf-8'))
    mb_size = byte_count / (1024 * 1024)
    
    return {
        'chars': char_count,
        'bytes': byte_count,
        'mb': mb_size
    }

def should_concatenate(current_content, new_content):
    """Decide se deve concatenar baseado no tamanho"""
    current_size = get_text_size_info(current_content)
    new_size = get_text_size_info(new_content)
    combined_size = get_text_size_info(current_content + new_content)
    
    # Se o arquivo atual é muito pequeno, sempre concatena
    if current_size['chars'] < MIN_FILE_SIZE_CHARS:
        return True
    
    # Se concatenar exceder o limite, não concatena
    if (combined_size['chars'] > MAX_FILE_SIZE_CHARS or 
        combined_size['mb'] > MAX_FILE_SIZE_MB):
        return False
    
    # Se o novo conteúdo é pequeno, concatena
    if new_size['chars'] < MIN_FILE_SIZE_CHARS:
        return True
    
    return False

def save_concatenated_file(content, filepath, source_urls):
    """Salva arquivo concatenado com metadados"""
    header = f"""# Documento Concatenado
Gerado automaticamente em: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total de fontes: {len(source_urls)}

## Fontes:
"""
    for i, source in enumerate(source_urls, 1):
        header += f"{i}. {source}\n"
    
    header += "\n" + "="*80 + "\n\n"
    
    full_content = header + content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    size_info = get_text_size_info(full_content)
    return size_info

# Scraping inicial
response = requests.get(url=url)
soup = BeautifulSoup(response.text, 'html.parser')
links = soup.find_all('a')

print("🔥 Links encontrados:")
print("=" * 40)

sublinks = set()

sublinks.add(url)

for link in links:
    href = link.get('href')
    if not href or href.startswith('#'):
        continue
    full_url = urljoin(url, href)
    sublinks.add(full_url)

sources = list(sublinks)
print(f"\n✅ Total: {len(sources)} links!")
print(f"📁 Arquivos serão salvos em: {output_dir}/")

# Inicialização para concatenação
converter = DocumentConverter()
filename_counter = defaultdict(int)
arquivos_processados = 0

# Variáveis para concatenação
current_batch_content = ""
current_batch_sources = []
batch_number = 1
individual_files = []  # Para arquivos grandes que ficam separados

for i, source in enumerate(sources, 1):
    try:
        print(f"\n[{i}/{len(sources)}] Processando: {source}")
        
        doc = converter.convert(source=source)
        md_content = doc.document.export_to_markdown()
        
        if not md_content.strip():
            print("   ⚠️  Conteúdo vazio, pulando...")
            continue
        
        size_info = get_text_size_info(md_content)
        
        # Adicionar separador e fonte ao conteúdo
        content_with_header = f"\n\n{'='*60}\n"
        content_with_header += f"# FONTE: {source}\n"
        content_with_header += f"{'='*60}\n\n"
        content_with_header += md_content
        
        # Decidir se concatena ou salva individualmente
        if size_info['chars'] > MAX_FILE_SIZE_CHARS or size_info['mb'] > MAX_FILE_SIZE_MB:
            # Arquivo muito grande - salvar individualmente
            parsed_url = urlparse(source)
            url_parts = parsed_url.path.strip('/').split('/')
            
            if len(url_parts) >= 2:
                base_name = '_'.join(url_parts[-2:])
            elif len(url_parts) == 1:
                base_name = url_parts[0]
            else:
                base_name = "documento_grande"
            
            base_name = re.sub(r'[\\/*?:"<>|#]', "_", base_name)[:100]
            filename = f"INDIVIDUAL_{base_name}.md"
            filepath = os.path.join(output_dir, filename)
            
            # Evitar sobrescrita
            counter = 1
            while os.path.exists(filepath):
                name_part = filename.replace('.md', '')
                filepath = os.path.join(output_dir, f"{name_part}_v{counter:02d}.md")
                counter += 1
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Documento Individual (Arquivo Grande)\n")
                f.write(f"Fonte: {source}\n")
                f.write(f"Tamanho: {size_info['chars']:,} caracteres\n\n")
                f.write(md_content)
            
            individual_files.append(filepath)
            print(f"   💾 Salvo individualmente: {os.path.basename(filepath)}")
            
        elif should_concatenate(current_batch_content, content_with_header):
            # Adicionar ao batch atual
            current_batch_content += content_with_header
            current_batch_sources.append(source)
            print(f"   📦 Adicionado ao batch {batch_number}")
            
        else:
            # Salvar batch atual e iniciar novo
            if current_batch_content:
                batch_filename = f"BATCH_{batch_number:03d}_concatenado.md"
                batch_filepath = os.path.join(output_dir, batch_filename)
                
                batch_size = save_concatenated_file(
                    current_batch_content, 
                    batch_filepath, 
                    current_batch_sources
                )
                
                batch_number += 1
            
            # Iniciar novo batch
            current_batch_content = content_with_header
            current_batch_sources = [source]
            print(f"   📦 Iniciado novo batch {batch_number}")
        
        arquivos_processados += 1
        
    except Exception as e:
        print(f'   ❌ Erro ao processar: {e}')

# Salvar último batch se houver conteúdo
if current_batch_content:
    batch_filename = f"BATCH_{batch_number:03d}_concatenado.md"
    batch_filepath = os.path.join(output_dir, batch_filename)
    
    batch_size = save_concatenated_file(
        current_batch_content, 
        batch_filepath, 
        current_batch_sources
    )

# Relatório final
print(f"\n🎉 PROCESSAMENTO CONCLUÍDO!")
print(f"📊 Estatísticas:")
print(f"   • {arquivos_processados} páginas processadas")
print(f"   • {batch_number} arquivos concatenados")
print(f"   • {len(individual_files)} arquivos individuais (grandes)")
print(f"   • Total de arquivos: {batch_number + len(individual_files)}")
print(f"\n📁 Arquivos salvos em: {output_dir}/")
