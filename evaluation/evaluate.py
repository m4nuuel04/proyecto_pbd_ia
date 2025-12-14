import sys
import os

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.sql_agent import run_sql_agent
from tabulate import tabulate
import time

# Define test cases - ajustados a la estructura real de la BD
TEST_CASES_SQL = [
    # Consultas simples (COUNT) - 4 casos
    "¿Cuántos usuarios hay en total?",
    "¿Cuántos pedidos hay en total?",
    "¿Cuántos productos hay en la categoría Electronics?",
    "¿Cuántos pedidos están en estado Delivered?",
    
    # Consultas con JOIN - 4 casos
    "¿Cuánto dinero ha gastado en total el usuario con username alice?",
    "Lista los nombres de usuario (username) que han hecho pedidos",
    "Muestra el username y email de usuarios que tienen pedidos en estado Pending",
    "¿Cuántos pedidos ha realizado cada usuario? Muestra username y cantidad",
    
    # Agregación (SUM, AVG) - 4 casos
    "¿Cuál es el importe total de todos los pedidos?",
    "¿Cuál es el precio promedio de todos los productos?",
    "¿Cuál es el importe promedio de los pedidos en estado Delivered?",
    "¿Cuál es el gasto total por cada método de pago?",
    
    # Filtrado complejo - 3 casos
    "Lista los productos con precio mayor a 100 y stock menor a 50",
    "Muestra los pedidos de los últimos 30 días con importe mayor a 200",
    "¿Cuáles son los 5 productos más caros de la categoría Electronics?",
]

def evaluate():
    results = []
    
    print("--- Evaluating SQL Agent (Ollama) ---")
    for query in TEST_CASES_SQL:
        print(f"Running: {query}")
        start = time.time()
        response_dict = run_sql_agent(query)
        
        if response_dict.get("error"):
             status = "FAILED"
             # Acortar errores para que no descuadren la tabla
             error_msg = response_dict["error"]
             response_summary = error_msg if len(error_msg) < 50 else error_msg[:47] + "..."
        else:
             status = "SUCCESS"
             answer = response_dict["answer"]
             # Acortar respuestas para que quepan bien en la tabla
             response_summary = answer if len(answer) < 50 else answer[:47] + "..."
        
        duration = time.time() - start
        results.append(["SQL", query, status, response_summary, f"{duration:.2f}s"])
        print(f"Result: {response_dict.get('answer', 'No answer')}\n")

    print("\n--- Final Summary ---")
    # Usar formato simple que se copia mejor en Word
    print(tabulate(results, headers=["Agent", "Query", "Status", "Response", "Time"], tablefmt="simple"))

if __name__ == "__main__":
    evaluate()
