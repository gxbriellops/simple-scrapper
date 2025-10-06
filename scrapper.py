#!/usr/bin/env python3
"""Web Scraper Simplificado - Extrai conteúdo de websites e converte para Markdown"""

import os
import re
from abc import ABC, abstractmethod
from urllib.parse import urlparse, urljoin
from datetime import datetime
from typing import List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter


# SOLID: Interface Segregation Principle - Interface para conversão de conteúdo
class IContentConverter(ABC):
    """Interface para conversores de conteúdo"""

    @abstractmethod
    def convert(self, url: str) -> str:
        """Converte conteúdo de uma URL para markdown"""
        pass


# SOLID: Dependency Inversion - Implementação concreta da interface
class DoclingConverter(IContentConverter):
    """Conversor de conteúdo usando Docling"""

    def __init__(self):
        self.converter = DocumentConverter()

    def convert(self, url: str) -> str:
        """Converte conteúdo de uma URL para markdown usando Docling"""
        return self.converter.convert(source=url).document.export_to_markdown()


# SOLID: Single Responsibility - Responsável apenas por gerenciar arquivos
class FileManager:
    """Gerencia operações de arquivos e diretórios"""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_content(self, filename: str, content: str, url: str) -> str:
        """Salva conteúdo em arquivo com metadados"""
        filepath = self._get_unique_filepath(filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {self._get_page_title(url)}\n\n")
            f.write(f"**Fonte:** {url}\n")
            f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write('='*80 + '\n\n')
            f.write(content)

        return os.path.basename(filepath)

    def _get_unique_filepath(self, filename: str) -> str:
        """Retorna um caminho de arquivo único (evita sobrescrever)"""
        filepath = os.path.join(self.output_dir, filename)
        counter = 1
        original_filepath = filepath

        while os.path.exists(filepath):
            name, ext = os.path.splitext(original_filepath)
            filepath = f"{name}_{counter:02d}{ext}"
            counter += 1

        return filepath

    def _get_page_title(self, url: str) -> str:
        """Extrai título da página da URL"""
        parsed = urlparse(url)
        if parsed.path and parsed.path != '/':
            title = parsed.path.strip('/').split('/')[-1]
            title = re.sub(r'\.(html?|php|asp|jsp)$', '', title)
            return title.replace('-', ' ').replace('_', ' ').title()
        return parsed.netloc

    @staticmethod
    def url_to_filename(url: str) -> str:
        """Converte URL em nome de arquivo válido"""
        parsed = urlparse(url)

        if parsed.path and parsed.path != '/':
            path = parsed.path.strip('/').replace('/', '_')
            path = re.sub(r'\.(html?|php|asp|jsp)$', '', path)
            filename = re.sub(r'[^\w\-_.]', '_', path)
            if filename:
                return f"{filename}.md"

        return f"{parsed.netloc.replace('.', '_')}.md"


# SOLID: Single Responsibility - Responsável apenas por criar índices
class IndexGenerator:
    """Gera índices de arquivos processados"""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def create_index(self, processed_files: List[Tuple[str, str]], source_urls: List[str]):
        """Cria arquivo de índice com informações dos arquivos processados"""
        index_path = os.path.join(self.output_dir, 'index.md')

        with open(index_path, 'w', encoding='utf-8') as f:
            title = "Múltiplos Sites" if len(source_urls) > 1 else urlparse(source_urls[0]).netloc

            f.write(f"# Índice - {title}\n\n")
            f.write(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**URLs de Origem:**\n")
            for url in source_urls:
                f.write(f"  - {url}\n")
            f.write(f"\n**Total de páginas:** {len(processed_files)}\n\n")
            f.write("## Arquivos Gerados:\n\n")

            for i, (url, filename) in enumerate(processed_files, 1):
                f.write(f"{i}. **{filename}** - {url}\n")

        print(f"   📑 Índice criado: index.md")


# SOLID: Single Responsibility - Responsável por processar URLs individuais
class URLProcessor:
    """Processa URLs individuais"""

    def __init__(self, converter: IContentConverter, file_manager: FileManager):
        self.converter = converter
        self.file_manager = file_manager

    def process(self, url: str) -> Optional[Tuple[str, str]]:
        """Processa uma URL e retorna tupla (url, filename) ou None se falhar"""
        try:
            print(f"📄 Processando: {url}")
            content = self.converter.convert(url)

            if not content.strip():
                return None

            filename = FileManager.url_to_filename(url)
            saved_filename = self.file_manager.save_content(filename, content, url)

            print(f"   💾 Salvo: {saved_filename}")
            return (url, saved_filename)

        except Exception as e:
            print(f"   ⚠️  Erro: {e}")
            return None


# SOLID: Dependency Injection - Classe orquestradora que usa composição
class SimpleWebScraper:
    """Orquestrador principal do processo de scraping"""

    def __init__(
        self,
        urls,
        use_selenium=False,
        max_pages=100,
        converter: Optional[IContentConverter] = None
    ):
        """
        Inicializa o scraper com injeção de dependências.

        Args:
            urls: URL única ou lista de URLs
            use_selenium: Flag para usar Selenium (não implementado ainda)
            max_pages: Limite de páginas a processar
            converter: Implementação de IContentConverter (opcional, usa DoclingConverter por padrão)
        """
        # Normalizar URLs para lista
        if isinstance(urls, str):
            self.urls = [urls]
        else:
            self.urls = urls

        self.use_selenium = use_selenium
        self.max_pages = max_pages

        # Definir output_dir padrão baseado na primeira URL
        domain = urlparse(self.urls[0]).netloc.replace('www.', '')
        self.output_dir = re.sub(r'[^\w\-_.]', '_', domain) or 'output'

        # SOLID: Dependency Injection - Permite injetar dependências
        self.converter = converter or DoclingConverter()
        self.file_manager = None  # Será criado quando output_dir for definido
        self.index_generator = None
        self.url_processor = None

    def _initialize_dependencies(self):
        """Inicializa dependências baseadas no output_dir"""
        self.file_manager = FileManager(self.output_dir)
        self.index_generator = IndexGenerator(self.output_dir)
        self.url_processor = URLProcessor(self.converter, self.file_manager)

    def get_links(self) -> List[str]:
        """Retorna lista de URLs a processar (limitada por max_pages)"""
        links = []
        for url in self.urls:
            links.append(url)
            if len(links) >= self.max_pages:
                break
        return links

    def run(self):
        """Executa o processo completo de scraping"""
        # Inicializar dependências
        self._initialize_dependencies()

        print(f"🚀 Iniciando scraping de {len(self.urls)} URL(s)\n📁 Salvando em: {self.output_dir}/\n")

        for url in self.urls:
            print(f"   🌐 {url}")
        print()

        links = self.get_links()
        print(f"🔗 {len(links)} links encontrados\n")

        # Processar links usando URLProcessor
        processed = []
        for link in links:
            result = self.url_processor.process(link)
            if result:
                processed.append(result)

        if not processed:
            print("\n❌ Nenhum conteúdo foi extraído")
            return

        # Criar índice usando IndexGenerator
        self.index_generator.create_index(processed, self.urls)
        print(f"\n✨ Concluído! {len(processed)} páginas processadas")


def main():
    url = 'https://docs.streamlit.io/develop/api-reference'
    scraper = SimpleWebScraper(url)
    scraper.run()


if __name__ == "__main__":
    main()