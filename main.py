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
    def __init__(self, url):
        self.url = url
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
        """Processa uma URL e salva em arquivo individual"""
        try:
            print(f"📄 Processando: {url}")
            content = self.converter.convert(source=url).document.export_to_markdown()
            
            if not content.strip():
                return None
                
            filename = self._url_to_filename(url)
            filepath = os.path.join(self.output_dir, filename)
            
            # Evitar sobrescrever arquivos com mesmo nome
            counter = 1
            original_filepath = filepath
            while os.path.exists(filepath):
                name, ext = os.path.splitext(original_filepath)
                filepath = f"{name}_{counter:02d}{ext}"
                counter += 1
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {self._get_page_title(url)}\n\n")
                f.write(f"**Fonte:** {url}\n")
                f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write('='*80 + '\n\n')
                f.write(content)
            
            print(f"   💾 Salvo: {os.path.basename(filepath)}")
            return (url, os.path.basename(filepath))
            
        except Exception as e:
            print(f"   ⚠️  Erro: {e}")
            return None
    
    def run(self):
        """Executa o scraping e salva os resultados"""
        print(f"🚀 Iniciando scraping de: {self.url}\n📁 Salvando em: {self.output_dir}/\n")
        
        links = self.get_links()
        print(f"🔗 {len(links)} links encontrados\n")
        
        # Processar links
        processed = [result for link in links if (result := self.process_url(link))]
        
        if not processed:
            print("\n❌ Nenhum conteúdo foi extraído")
            return
        
        # Criar índice
        self._create_index(processed)
        print(f"\n✨ Concluído! {len(processed)} páginas processadas")
    
    def _url_to_filename(self, url):
        """Converte URL em nome de arquivo válido"""
        parsed = urlparse(url)
        
        # Usar path da URL se disponível
        if parsed.path and parsed.path != '/':
            path = parsed.path.strip('/').replace('/', '_')
            path = re.sub(r'\.(html?|php|asp|jsp)$', '', path)
            filename = re.sub(r'[^\w\-_.]', '_', path)
            if filename:
                return f"{filename}.md"
        
        # Fallback para domain
        return f"{parsed.netloc.replace('.', '_')}.md"
    
    def _get_page_title(self, url):
        """Extrai título da página para usar como cabeçalho"""
        parsed = urlparse(url)
        if parsed.path and parsed.path != '/':
            title = parsed.path.strip('/').split('/')[-1]
            title = re.sub(r'\.(html?|php|asp|jsp)$', '', title)
            return title.replace('-', ' ').replace('_', ' ').title()
        return parsed.netloc
    
    def _create_index(self, processed_files):
        """Cria um índice com todos os arquivos processados"""
        with open(os.path.join(self.output_dir, 'index.md'), 'w', encoding='utf-8') as f:
            f.write(f"# Índice - {urlparse(self.url).netloc}\n\n")
            f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**URL Original:** {self.url}\n")
            f.write(f"**Total de páginas:** {len(processed_files)}\n\n")
            f.write("## Arquivos Gerados:\n\n")
            
            for i, (url, filename) in enumerate(processed_files, 1):
                f.write(f"{i}. **{filename}** - {url}\n")
        
        print(f"   📑 Índice criado: index.md")


def main():
    url = 'https://docs.streamlit.io/develop/api-reference'
    scraper = SimpleWebScraper(url)
    scraper.run()


if __name__ == "__main__":
    main()