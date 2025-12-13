import os
import argparse

# IMPORTANTE: Importar psycopg2_fix ANTES de cualquier agente que use psycopg2
from src.utils import psycopg2_fix

from src.utils.encoding_utils import safe_load_dotenv
from src.agents.sql_agent import run_sql_agent
from src.agents.mongo_agent import run_mongo_agent
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

safe_load_dotenv(verbose=True)

def process_query(query: str, db_type: str = "postgres"):
    """Processes a single query and prints the output."""
    # Silent execution, only output results
    
    if db_type == "postgres":
        print(f"{Fore.BLUE}Using PostgreSQL Agent...{Style.RESET_ALL}")
        result = run_sql_agent(query)
    elif db_type == "mongo":
        print(f"{Fore.GREEN}Using MongoDB Agent...{Style.RESET_ALL}")
        result = run_mongo_agent(query)
    else:
        print(f"{Fore.RED}Unknown DB type: {db_type}")
        return

    if result.get("error"):
        print(f"{Fore.RED}Error: {result['error']}")
    else:
        if result.get("sql_queries"):
            title = "Consulta Generada (SQL)" if db_type == "postgres" else "Código Generado (PyMongo)"
            print(f"\n{Fore.CYAN}--- {title} ---{Style.RESET_ALL}")
            for sql in result["sql_queries"]:
                print(f"{Fore.YELLOW}{sql}")
        
        if result.get("raw_results"):
            print(f"\n{Fore.CYAN}--- Respuesta Raw ---{Style.RESET_ALL}")
            for res in result["raw_results"]:
                print(f"{Fore.WHITE}{res}")

        print(f"\n{Fore.CYAN}--- Interpretación ---{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{result['answer']}\n")


def main():
    parser = argparse.ArgumentParser(description="Agente de Base de Datos LLM (PostgreSQL + MongoDB + Ollama)")
    parser.add_argument("--query", type=str, required=False, help="Consulta en lenguaje natural (opcional)")
    parser.add_argument("--db", type=str, default="postgres", choices=["postgres", "mongo"], help="Base de datos a usar (postgres o mongo)")
    
    args = parser.parse_args()
    
    current_db = args.db

    # Single-shot mode
    if args.query:
        process_query(args.query, current_db)
        return

    # Interactive mode
    print(f"{Fore.MAGENTA}🤖 Agente de Base de Datos LLM (Modo Interactivo)")
    print(f"{Fore.WHITE}Base de datos actual: {Fore.YELLOW}{current_db.upper()}")
    print(f"Escribe 'switch mongo' o 'switch postgres' para cambiar de DB.")
    print(f"Escribe 'salir' o 'exit' para terminar.\n")
    
    while True:
        try:
            user_input = input(f"{Fore.BLUE}[{current_db}] >> Introduce tu pregunta: {Style.RESET_ALL}").strip()
            
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "salir"]:
                print(f"{Fore.MAGENTA}¡Hasta la vista!")
                break
            
            if user_input.lower() in ["switch mongo", "use mongo"]:
                current_db = "mongo"
                print(f"{Fore.YELLOW}Cambiado a MongoDB.{Style.RESET_ALL}")
                continue
                
            if user_input.lower() in ["switch postgres", "use postgres"]:
                current_db = "postgres"
                print(f"{Fore.YELLOW}Cambiado a PostgreSQL.{Style.RESET_ALL}")
                continue

            process_query(user_input, current_db)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.MAGENTA}¡Hasta la vista!")
            break
        except Exception as e:
            print(f"{Fore.RED}Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
