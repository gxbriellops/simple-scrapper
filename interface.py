import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import List, Tuple, Optional
from scrapper import SimpleWebScraper


# SOLID: Single Responsibility - Responsável apenas por validação de inputs
class InputValidator:
    """Valida inputs do usuário"""

    @staticmethod
    def validate_urls(url_entries: List[ttk.Entry]) -> Optional[List[str]]:
        """Valida e retorna lista de URLs válidas ou None se houver erro"""
        urls = []
        for entry in url_entries:
            url = entry.get().strip()
            if url and url != "https://":
                if not url.startswith(('http://', 'https://')):
                    messagebox.showerror("Erro", f"A URL '{url}' deve começar com http:// ou https://")
                    return None
                urls.append(url)

        if not urls:
            messagebox.showerror("Erro", "Por favor, insira pelo menos uma URL válida!")
            return None

        return urls

    @staticmethod
    def validate_folder_name(folder_name: str) -> Optional[str]:
        """Valida nome da pasta ou None se inválido"""
        folder_name = folder_name.strip()

        # Remover texto de placeholder se presente
        if folder_name.startswith("Selecione ou digite") or folder_name.startswith("Digite o nome"):
            folder_name = ""

        if not folder_name:
            messagebox.showerror("Erro", "Por favor, insira um nome para a pasta!")
            return None

        return folder_name


# SOLID: Single Responsibility - Responsável por gerenciar pastas
class FolderManager:
    """Gerencia operações relacionadas a pastas"""

    def __init__(self, base_dir: str = "DOCUMENTAÇÃO"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def get_existing_folders(self) -> List[str]:
        """Retorna lista de pastas existentes no diretório base"""
        try:
            folders = [
                f for f in os.listdir(self.base_dir)
                if os.path.isdir(os.path.join(self.base_dir, f))
            ]
            folders.sort()
            return folders
        except Exception as e:
            print(f"Erro ao listar pastas: {e}")
            return []

    def create_folder(self, folder_name: str) -> str:
        """Cria pasta e retorna o caminho completo"""
        folder_path = os.path.join(self.base_dir, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path


# SOLID: Single Responsibility - Gerencia campos dinâmicos de URL
class URLFieldManager:
    """Gerencia criação e remoção de campos de URL"""

    def __init__(self, container: ttk.Frame):
        self.container = container
        self.url_entries: List[ttk.Entry] = []
        self.url_frames: List[ttk.Frame] = []

    def add_url_field(self):
        """Adiciona um novo campo de URL"""
        url_frame = ttk.Frame(self.container)
        url_frame.grid(row=len(self.url_frames), column=0, sticky=(tk.W, tk.E), pady=2)
        url_frame.columnconfigure(0, weight=1)

        # Entry para URL
        url_entry = ttk.Entry(url_frame, width=60, font=('Arial', 10))
        url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        url_entry.insert(0, " ")

        # Botão remover
        remove_btn = ttk.Button(
            url_frame,
            text="✖",
            width=3,
            command=lambda: self.remove_url_field(url_frame, url_entry)
        )
        remove_btn.grid(row=0, column=1)

        # Se for o primeiro campo, esconder botão remover
        if len(self.url_entries) == 0:
            remove_btn.grid_remove()

        self.url_entries.append(url_entry)
        self.url_frames.append(url_frame)

        self._update_remove_buttons()

    def remove_url_field(self, frame: ttk.Frame, entry: ttk.Entry):
        """Remove um campo de URL"""
        if len(self.url_entries) <= 1:
            return  # Não permitir remover o último campo

        if entry in self.url_entries:
            self.url_entries.remove(entry)
        if frame in self.url_frames:
            self.url_frames.remove(frame)

        frame.destroy()

        # Reposicionar os frames restantes
        for i, url_frame in enumerate(self.url_frames):
            url_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)

        self._update_remove_buttons()

    def _update_remove_buttons(self):
        """Atualiza a visibilidade dos botões de remover"""
        show_buttons = len(self.url_entries) > 1

        for frame in self.url_frames:
            for widget in frame.winfo_children():
                if isinstance(widget, ttk.Button) and widget.cget('text') == '✖':
                    if show_buttons:
                        widget.grid()
                    else:
                        widget.grid_remove()

    def get_entries(self) -> List[ttk.Entry]:
        """Retorna lista de entries de URL"""
        return self.url_entries


# SOLID: Single Responsibility - Responsável apenas pela interface gráfica
class WebScraperGUI:
    """Interface gráfica para o Web Scraper"""

    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper - Documentação")
        self.root.geometry("750x750")
        self.root.resizable(True, True)

        # SOLID: Dependency Injection - Injetar dependências
        self.folder_manager = FolderManager()
        self.url_field_manager = None  # Será criado após criar o container

        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurar grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Título
        title = ttk.Label(main_frame, text="📄 Web Scraper", font=('Arial', 18, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        self.current_row = 1

        # Frame container para URLs
        ttk.Label(main_frame, text="URLs dos Sites:", font=('Arial', 10, 'bold')).grid(row=self.current_row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        self.current_row += 1

        # Frame scrollável para URLs
        urls_container = ttk.Frame(main_frame)
        urls_container.grid(row=self.current_row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        urls_container.columnconfigure(0, weight=1)
        self.current_row += 1

        # SOLID: Usar URLFieldManager para gerenciar campos de URL
        self.url_field_manager = URLFieldManager(urls_container)
        self.url_field_manager.add_url_field()

        # Botão para adicionar mais URLs
        add_url_btn = ttk.Button(main_frame, text="➕ Adicionar URL", command=self.url_field_manager.add_url_field)
        add_url_btn.grid(row=self.current_row, column=0, columnspan=2, pady=5)
        self.current_row += 1

        # Salvar referência ao main_frame
        self.main_frame = main_frame

        # Nome da pasta (com seleção de pastas existentes)
        ttk.Label(main_frame, text="Nome da Pasta:", font=('Arial', 10)).grid(row=self.current_row, column=0, sticky=tk.W, pady=5)

        # Frame para combobox e botão refresh
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=self.current_row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        folder_frame.columnconfigure(0, weight=1)

        # Combobox para selecionar ou criar pasta
        self.folder_combo = ttk.Combobox(folder_frame, width=47, font=('Arial', 10))
        self.folder_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        # Botão para atualizar lista de pastas
        refresh_btn = ttk.Button(folder_frame, text="🔄", width=3, command=self.refresh_folders)
        refresh_btn.grid(row=0, column=1)

        # Carregar pastas existentes
        self.refresh_folders()

        self.current_row += 1

        # Limite de páginas
        # ttk.Label(main_frame, text="Limite de Páginas:", font=('Arial', 10)).grid(row=self.current_row, column=0, sticky=tk.W, pady=5)
        # self.max_pages_var = tk.StringVar(value="100")
        # max_pages_frame = ttk.Frame(main_frame)
        # max_pages_frame.grid(row=self.current_row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        # self.max_pages_spinbox = ttk.Spinbox(max_pages_frame, from_=1, to=1000, textvariable=self.max_pages_var, width=10, font=('Arial', 10))
        # self.max_pages_spinbox.pack(side=tk.LEFT)
        # ttk.Label(max_pages_frame, text=" páginas (máximo a processar)", font=('Arial', 9), foreground='gray').pack(side=tk.LEFT, padx=(5, 0))
        # self.current_row += 1

        # Selenium
        selenium_frame = ttk.Frame(main_frame)
        selenium_frame.grid(row=self.current_row, column=0, columnspan=2, pady=(10, 5))
        self.selenium_var = tk.BooleanVar(value=True)
        self.selenium_check = ttk.Checkbutton(
            selenium_frame,
            text="🌐 Usar Selenium (para sites dinâmicos/JavaScript)",
            variable=self.selenium_var,
            style='TCheckbutton'
        )
        self.selenium_check.pack()
        self.current_row += 1

        # Botão executar
        self.run_button = ttk.Button(main_frame, text="🚀 Iniciar Scraping", command=self.start_scraping)
        self.run_button.grid(row=self.current_row, column=0, columnspan=2, pady=20)
        self.current_row += 1

        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=self.current_row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.current_row += 1

        # Label de status
        self.status_label = ttk.Label(main_frame, text="Pronto para iniciar", font=('Arial', 9), foreground='gray')
        self.status_label.grid(row=self.current_row, column=0, columnspan=2, pady=(0, 10))
        self.current_row += 1

        # Área de log
        ttk.Label(main_frame, text="Log de Atividades:", font=('Arial', 10, 'bold')).grid(row=self.current_row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        self.current_row += 1

        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=70, font=('Consolas', 9), bg='#f5f5f5')
        self.log_text.grid(row=self.current_row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Configurar expansão do log
        main_frame.rowconfigure(self.current_row, weight=1)
        self.current_row += 1

        # Botão limpar log
        clear_button = ttk.Button(main_frame, text="Limpar Log", command=self.clear_log)
        clear_button.grid(row=self.current_row, column=0, columnspan=2, pady=(0, 10))

        # Redirecionar stdout para o log
        sys.stdout = TextRedirector(self.log_text)

        self.log("Bem-vindo ao Web Scraper!")
        self.log("Preencha a URL e o nome da pasta para começar.\n")

    def log(self, message):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def clear_log(self):
        """Limpa o log"""
        self.log_text.delete(1.0, tk.END)

    def refresh_folders(self):
        """Atualiza a lista de pastas existentes usando FolderManager"""
        folders = self.folder_manager.get_existing_folders()

        # Atualizar o combobox com as pastas
        self.folder_combo['values'] = folders

        # Se houver pastas, mostrar uma dica
        if folders:
            self.folder_combo.set(f"Selecione ou digite um nome ({len(folders)} pastas existentes)")
        else:
            self.folder_combo.set("Digite o nome da pasta")

    def validate_inputs(self) -> Tuple[Optional[List[str]], Optional[str]]:
        """Valida os inputs do usuário usando InputValidator"""
        # SOLID: Usar InputValidator para validação
        urls = InputValidator.validate_urls(self.url_field_manager.get_entries())
        if urls is None:
            return None, None

        folder_name = InputValidator.validate_folder_name(self.folder_combo.get())
        if folder_name is None:
            return None, None

        return urls, folder_name

    def start_scraping(self):
        """Inicia o processo de scraping em uma thread separada"""
        urls, folder_name = self.validate_inputs()
        if not urls or not folder_name:
            return

        # Desabilitar botão
        self.run_button.config(state='disabled')
        self.progress.start(10)
        self.status_label.config(text="Processando...", foreground='blue')

        # Executar em thread separada para não travar a interface
        thread = threading.Thread(target=self.run_scraper, args=(urls, folder_name))
        thread.daemon = True
        thread.start()

    def run_scraper(self, urls: List[str], folder_name: str):
        """Executa o scraper usando injeção de dependências"""
        try:
            # Obter configurações
            use_selenium = self.selenium_var.get()
            max_pages = int(self.max_pages_var.get())

            # SOLID: Usar FolderManager para criar pasta
            folder_path = self.folder_manager.create_folder(folder_name)

            self.log(f"\n{'='*60}")
            self.log(f"Iniciando scraping de {len(urls)} URL(s)")
            for url in urls:
                self.log(f"  🌐 {url}")
            self.log(f"Pasta de destino: {folder_path}/")
            self.log(f"Selenium: {'Ativado' if use_selenium else 'Desativado'}")
            self.log(f"Limite de páginas: {max_pages}")
            self.log(f"{'='*60}\n")

            # SOLID: Criar instância do scraper com injeção de dependências
            scraper = SimpleWebScraper(
                urls,
                use_selenium=use_selenium,
                max_pages=max_pages
            )

            # Configurar output_dir
            scraper.output_dir = folder_path

            # Executar scraping
            scraper.run()

            self.log(f"\n{'='*60}")
            self.log(f"✅ Scraping concluído com sucesso!")
            self.log(f"📁 Arquivos salvos em: {scraper.output_dir}/")
            self.log(f"{'='*60}\n")

            # Atualizar interface
            self.root.after(0, self.scraping_complete, True)

        except Exception as e:
            self.log(f"\n❌ ERRO: {str(e)}\n")
            self.root.after(0, self.scraping_complete, False)

    def scraping_complete(self, success):
        """Chamado quando o scraping termina"""
        self.progress.stop()
        self.run_button.config(state='normal')

        if success:
            self.status_label.config(text="✅ Concluído com sucesso!", foreground='green')
            # Atualizar lista de pastas
            self.refresh_folders()
            messagebox.showinfo("Sucesso", "Scraping concluído com sucesso!")
        else:
            self.status_label.config(text="❌ Erro durante o processo", foreground='red')
            messagebox.showerror("Erro", "Ocorreu um erro durante o scraping. Verifique o log.")


class TextRedirector:
    """Redireciona stdout para um widget Text"""
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.insert(tk.END, text)
        self.widget.see(tk.END)

    def flush(self):
        pass


def main():
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()