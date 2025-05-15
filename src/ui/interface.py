from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from src.rag.retriever import Retriever
from src.rag.generator import Generator
import sys
import termios
import tty
import os
import sqlite3

class ChatbotInterface:
    def __init__(self, retriever=None, generator=None):
        self.console = Console()
        try:
            self.retriever = retriever or Retriever()
            self.generator = generator or Generator(model_name="gpt-4o-mini-2024-07-18")
            self.create_db()  
        except Exception as e:
            self.console.print(f"[red]Error initializing RAG system: {str(e)}[/red]")
            sys.exit(1)
        self.history = []
        self.current_input = ""
        self.clear_screen()
        self.display_welcome()

    def create_db(self):
        self.db_conn = sqlite3.connect("chat_history.db")
        cursor = self.db_conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query TEXT,
                answer TEXT
            )
        """)
        self.db_conn.commit()

    def db_logs(self, query: str, answer: str):
        cursor = self.db_conn.cursor()
        cursor.execute("INSERT INTO interactions (query, answer) VALUES (?, ?)", (query, answer))
        self.db_conn.commit()

    def display_welcome(self):
        welcome_message = """
        Welcome to <tinypilot>!
        
        Ask questions about the tinygrad codebase, or bounties.
        Examples:
        - What is lazy evaluation in tinygrad?
        - Show me the latest bounties
        - How does the backward pass work?
        
        Commands:
        - 'clear' to clear history
        - 'exit' to quit
        """
        self.console.print(Panel(welcome_message, title="Welcome", border_style="green"))

    def display_history(self):
        for q, r in self.history[-10:]:
            self.console.print(f"[bold cyan]You:[/bold cyan] {q}")
            self.console.print(f"[bold green]tinypilot:[/bold green] {r}\n")

    def get_input(self):
        self.current_input = ""
        self.console.print("> ", end="", style="bold")
        
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            while True:
                char = sys.stdin.read(1)
                if char == '\r' or char == '\n': 
                    print()  
                    return self.current_input
                
                elif char == '\x7f':  
                    if self.current_input:
                        self.current_input = self.current_input[:-1]
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                
                elif char.isprintable():
                    self.current_input += char
                    sys.stdout.write(char)
                    sys.stdout.flush()
                
                elif char == '\x03': 
                    raise KeyboardInterrupt
                
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def clear_history(self):
        self.history = []
        self.clear_screen()
        self.display_welcome()
        self.console.print("[yellow]History cleared[/yellow]")

    def run(self):
        while True:
            query = self.get_input().strip()
            
            if query.lower() == "exit":
                self.console.print("[bold yellow]Goodbye![/bold yellow]")
                if hasattr(self, 'db_conn') and self.db_conn:
                    self.db_conn.close()
                break
            elif query.lower() == "clear":
                self.clear_history()
                continue

            if not query:
                self.console.print("[red]Please enter a valid question or command.[/red]")
                continue

            try:
                with Progress(transient=True) as progress:
                    task = progress.add_task("[cyan]Processing query...", total=None)
                    
                    docs = self.retriever.retrieve(query)
                    response = self.generator.generate(query, docs)
                    self.history.append((query, response))
                    self.db_logs(query, response)
                    
                    self.clear_screen()
                    self.display_welcome()
                    self.display_history()
                    
            except Exception as e:
                error_msg = f"[red]Error processing query: {str(e)}[/red]"
                self.history.append((query, error_msg))
                self.db_logs(query, error_msg)
                self.console.print(f"[red]An error occurred. Please try again.[/red]") 