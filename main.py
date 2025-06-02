#!/usr/bin/env python3
"""Web Scraper Simplificado - Extrai conteúdo de websites e converte para Markdown"""

import os
import re
from urllib.parse import urlparse, urljoin
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter


class SimpleWebScraper:
    def __init__(self, url, max_files=10):
        self.url = url
        self.max_files = max_files
        self.converter = DocumentConverter()
        
        domain = urlparse(url).netloc.replace('www.', '')
        self.output_dir = re.sub(r'[^\w\-_.]', '_', domain) or 'output'
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_links(self):
        """Obtém todos os links da mesma domain"""
        try:
            soup = BeautifulSoup(requests.get(self.url, timeout=30).text, 'html.parser')
            base_domain = urlparse(self.url).netloc
            
            links = {self.url}
            links.update(urljoin(self.url, a['href']) 
                        for a in soup.find_all('a', href=True)
                        if urlparse(urljoin(self.url, a['href'])).netloc == base_domain)
            return list(links)
        except Exception as e:
            print(f"❌ Erro ao obter links: {e}")
            return [self.url]
    
    def process_url(self, url):
        """Processa uma URL e retorna o conteúdo em Markdown"""
        try:
            print(f"📄 Processando: {url}")
            content = self.converter.convert(source=url).document.export_to_markdown()
            return (url, content) if content.strip() else None
        except Exception as e:
            print(f"   ⚠️  Erro: {e}")
            return None
    
    def run(self):
        """Executa o scraping e salva os resultados"""
        print(f"🚀 Iniciando scraping de: {self.url}\n📁 Salvando em: {self.output_dir}/\n")
        
        links = self.get_links()
        print(f"🔗 {len(links)} links encontrados\n")
        
        # Processar links e coletar conteúdo
        all_content = [result for link in links if (result := self.process_url(link))]
        
        if not all_content:
            print("\n❌ Nenhum conteúdo foi extraído")
            return
        
        # Salvar e concatenar conteúdo
        self._save_concatenated(all_content)
        print(f"\n✨ Concluído! {len(all_content)} páginas processadas")
    
    def _save_concatenated(self, content_list):
        """Salva o conteúdo em arquivos concatenados"""
        concat_files = max(1, (len(content_list) + 9) // 10)  # Máximo 10 arquivos finais
        groups = [content_list[i:i + concat_files] for i in range(0, len(content_list), concat_files)]
        
        concatenated_info = {}
        for idx, group in enumerate(groups, 1):
            filename = f"concat_{idx:02d}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Cabeçalho
                f.write(f"# Arquivo Concatenado {idx}\n")
                f.write(f"# Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Contém {len(group)} páginas:\n")
                
                urls = []
                for url, _ in group:
                    f.write(f"# - {self._url_to_filename(url)} ({url})\n")
                    urls.append(url)
                
                f.write("\n" + "="*100 + "\n\n")
                
                # Conteúdo
                for i, (url, content) in enumerate(group, 1):
                    if i > 1:
                        f.write("\n\n" + "-"*80 + "\n\n")
                    f.write(f"## PÁGINA {i}: {self._url_to_filename(url)}\n\n")
                    f.write(f"# Fonte: {url}\n")
                    f.write(f"# Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write('='*80 + '\n\n')
                    f.write(content)
            
            concatenated_info[filename] = urls
            print(f"   💾 Salvo: {filename}")
        
        # Criar índice
        self._create_index(concatenated_info)
    
    def _url_to_filename(self, url):
        """Converte URL em nome de arquivo válido"""
        parsed = urlparse(url)
        
        if parsed.path and parsed.path != '/':
            path = parsed.path.strip('/')
            path = re.sub(r'\.(html?|php|asp|jsp)$', '', path)
            path = re.sub(r'[_\-\.]', ' ', path)
            filename = os.path.basename(path.strip())
            if filename:
                return f"{filename}.md"
        
        return f"{parsed.netloc}.md"
    
    def _create_index(self, concatenated_info):
        """Cria um índice final com os arquivos concatenados"""
        with open(os.path.join(self.output_dir, 'index.md'), 'w', encoding='utf-8') as f:
            f.write(f"# Índice Final - {urlparse(self.url).netloc}\n\n")
            f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**URL Original:** {self.url}\n")
            f.write(f"**Total de arquivos:** {len(concatenated_info)}\n\n")
            f.write("## Arquivos Concatenados:\n\n")
            
            for filename, urls in concatenated_info.items():
                f.write(f"### 📄 {filename}\n")
                f.write(f"**Páginas incluídas:** {len(urls)}\n\n")
                for i, url in enumerate(urls, 1):
                    f.write(f"{i}. {url}\n")
                f.write("\n")
        
        print(f"   📑 Índice criado: index.md")


def main():
    url = 'https://docs.streamlit.io/develop/api-reference'
    scraper = SimpleWebScraper(url)
    scraper.run()


if __name__ == "__main__":
    main()