import requests
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter
import re
import os
from urllib.parse import urlparse
from collections import defaultdict

url = 'https://docs.streamlit.io/'
output_dir = 'streamlit_docs'

# Criar o diretório se não existir
os.makedirs(output_dir, exist_ok=True)

response = requests.get(url=url)
soup = BeautifulSoup(response.text, 'html.parser')
links = soup.find_all('a')

# Filtrar e mostrar
print("🔥 Links com exemplos de código:")
print("=" * 40)

sublinks = []
for link in links:
    href = link.get('href')
    
    if href and href.startswith('./'):
        full_url = f'{url}{href[2:]}'
    elif href and href.startswith('/'):
        full_url = f'https://docs.streamlit.io{href}'
    elif href and href.startswith('http'):
        full_url = href
    else:
        continue
    
    if full_url not in sublinks:
        sublinks.append(full_url)
        print(full_url)

sources = sublinks

print(f"\n✅ Total: {len(sources)} links!")
print(f"📁 Arquivos serão salvos em: {output_dir}/")

converter = DocumentConverter()
filename_counter = defaultdict(int)  # Contador para nomes duplicados

for source in sources:
    try:
        doc = converter.convert(source=source)
        md_content = doc.document.export_to_markdown()
        
        # Estratégia 1: Usar partes da URL para nome único
        parsed_url = urlparse(source)
        url_parts = parsed_url.path.strip('/').split('/')
        
        # Pegar as últimas 2-3 partes da URL para o nome
        if len(url_parts) >= 2:
            base_name = '_'.join(url_parts[-2:])
        elif len(url_parts) == 1:
            base_name = url_parts[0]
        else:
            # Fallback: usar primeira linha do markdown
            first_line = md_content.splitlines()[0].strip() if md_content.splitlines() else "documento"
            base_name = re.sub(r'[\\/*?:"<>|#]', "", first_line)
        
        # Limpar caracteres inválidos
        base_name = re.sub(r'[\\/*?:"<>|#]', "_", base_name)
        base_name = base_name[:100]  # Limitar tamanho
        
        if not base_name or base_name.isspace():
            base_name = "documento"
        
        # Estratégia 2: Adicionar contador para duplicados
        filename_counter[base_name] += 1
        
        if filename_counter[base_name] > 1:
            filename = f"{base_name}_{filename_counter[base_name]:02d}.md"
        else:
            filename = f"{base_name}.md"
        
        # Caminho completo
        filepath = os.path.join(output_dir, filename)
        
        # Estratégia 3: Verificação adicional se arquivo já existe
        counter = 1
        original_filepath = filepath
        while os.path.exists(filepath):
            name_part = filename.replace('.md', '')
            filepath = os.path.join(output_dir, f"{name_part}_v{counter:02d}.md")
            counter += 1

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f'✅ Arquivo salvo: "{filepath}"')
        print(f'   📍 Fonte: {source}')
        
    except Exception as e:
        print(f'❌ Erro ao processar "{source}": {e}')

print(f"\n🎉 Processamento concluído! Arquivos salvos em: {output_dir}/")