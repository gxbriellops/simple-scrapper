# Princípios SOLID Aplicados

Este documento descreve como os princípios SOLID foram aplicados no projeto Web Scraper.

## 📋 Resumo dos Princípios SOLID

### S - Single Responsibility Principle (Princípio da Responsabilidade Única)
Cada classe deve ter apenas uma razão para mudar.

### O - Open/Closed Principle (Princípio Aberto/Fechado)
Classes devem estar abertas para extensão, mas fechadas para modificação.

### L - Liskov Substitution Principle (Princípio da Substituição de Liskov)
Subtipos devem poder substituir seus tipos base sem alterar o comportamento.

### I - Interface Segregation Principle (Princípio da Segregação de Interface)
Clientes não devem depender de interfaces que não usam.

### D - Dependency Inversion Principle (Princípio da Inversão de Dependência)
Dependa de abstrações, não de implementações concretas.

---

## 🔧 Aplicação no scrapper.py

### 1. **IContentConverter** (Interface)
- **Princípios**: Interface Segregation + Dependency Inversion
- **Responsabilidade**: Define contrato para conversão de conteúdo
- **Benefício**: Permite trocar implementações de conversor sem modificar código cliente

```python
class IContentConverter(ABC):
    @abstractmethod
    def convert(self, url: str) -> str:
        pass
```

### 2. **DoclingConverter**
- **Princípios**: Single Responsibility + Dependency Inversion
- **Responsabilidade**: Converter conteúdo usando biblioteca Docling
- **Benefício**: Pode ser substituído por outros conversores (BeautifulSoup, Selenium, etc.)

### 3. **FileManager**
- **Princípios**: Single Responsibility
- **Responsabilidade**: Gerenciar operações de arquivo (salvar, criar nomes únicos)
- **Benefício**: Centraliza lógica de persistência, facilitando testes e manutenção

### 4. **IndexGenerator**
- **Princípios**: Single Responsibility
- **Responsabilidade**: Criar arquivos de índice
- **Benefício**: Separação clara de concerns, fácil de testar isoladamente

### 5. **URLProcessor**
- **Princípios**: Single Responsibility + Dependency Injection
- **Responsabilidade**: Processar URLs individuais
- **Benefício**: Recebe dependências via construtor, facilitando testes unitários

### 6. **SimpleWebScraper** (Orquestrador)
- **Princípios**: Open/Closed + Dependency Injection
- **Responsabilidade**: Orquestrar processo completo de scraping
- **Benefício**: Aceita injeção de dependências, permitindo extensão sem modificação

```python
scraper = SimpleWebScraper(
    urls,
    converter=CustomConverter()  # Pode injetar qualquer implementação de IContentConverter
)
```

---

## 🎨 Aplicação no interface.py

### 1. **InputValidator**
- **Princípios**: Single Responsibility
- **Responsabilidade**: Validar inputs do usuário (URLs e nomes de pasta)
- **Benefício**: Lógica de validação isolada e reutilizável

### 2. **FolderManager**
- **Princípios**: Single Responsibility
- **Responsabilidade**: Gerenciar operações de pastas (listar, criar)
- **Benefício**: Centraliza operações de sistema de arquivos

### 3. **URLFieldManager**
- **Princípios**: Single Responsibility
- **Responsabilidade**: Gerenciar campos dinâmicos de URL na interface
- **Benefício**: Encapsula lógica de UI complexa

### 4. **WebScraperGUI**
- **Princípios**: Single Responsibility + Dependency Injection
- **Responsabilidade**: Coordenar interface gráfica
- **Benefício**: Delega responsabilidades específicas para classes especializadas

---

## 🎯 Benefícios Obtidos

### ✅ Testabilidade
- Classes pequenas com responsabilidades únicas são mais fáceis de testar
- Injeção de dependências permite mockar componentes

### ✅ Manutenibilidade
- Mudanças em uma funcionalidade afetam apenas uma classe
- Código mais organizado e fácil de entender

### ✅ Extensibilidade
- Novos conversores podem ser adicionados implementando `IContentConverter`
- Novos validadores podem ser criados sem modificar código existente

### ✅ Reusabilidade
- Classes como `FileManager` e `InputValidator` podem ser reutilizadas em outros projetos

---

## 🔄 Exemplo de Extensão

### Adicionar novo conversor (Selenium):

```python
class SeleniumConverter(IContentConverter):
    def __init__(self):
        self.driver = webdriver.Chrome()

    def convert(self, url: str) -> str:
        self.driver.get(url)
        # Extrair conteúdo usando Selenium
        return markdown_content

# Usar o novo conversor
scraper = SimpleWebScraper(
    urls,
    converter=SeleniumConverter()  # Injeção de dependência
)
```

### Adicionar novo validador:

```python
class EmailValidator:
    @staticmethod
    def validate_email(email: str) -> Optional[str]:
        if '@' not in email:
            messagebox.showerror("Erro", "Email inválido")
            return None
        return email
```

---

## 📚 Referências

- [SOLID Principles - Wikipedia](https://en.wikipedia.org/wiki/SOLID)
- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [Design Patterns: Elements of Reusable Object-Oriented Software](https://www.amazon.com/Design-Patterns-Elements-Reusable-Object-Oriented/dp/0201633612)
