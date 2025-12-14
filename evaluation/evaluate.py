import sys
import os

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.sql_agent import run_sql_agent
from src.agents.mongo_agent import run_mongo_agent
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

# Define test cases para MongoDB - ajustados a la estructura real
TEST_CASES_MONGO = [
    # Consultas simples (COUNT) - 4 casos
    "¿Cuántos usuarios hay en total?",
    "¿Cuántos pedidos hay en total?",
    "¿Cuántos pedidos hay en estado completed?",
    "¿Cuántos pedidos hay en estado pending?",
    
    # Consultas con filtrado - 5 casos
    "Muestra los pedidos de Alice Smith",
    "Lista los usuarios cuyo email contiene 'example.com'",
    "Muestra todos los pedidos del producto Laptop",
    "Lista los pedidos con importe mayor a 100",
    "Muestra los usuarios cuyo nombre empieza con 'B'",
    
    # Agregación (SUM, AVG) - 4 casos
    "¿Cuál es el importe total de todos los pedidos?",
    "¿Cuál es el importe promedio de los pedidos?",
    "¿Cuál es el importe total de pedidos en estado completed?",
    "¿Cuánto ha gastado cada usuario? Muestra nombre y total",
    
    # Filtrado y ordenamiento - 2 casos
    "Muestra los 5 pedidos con mayor importe",
    "Lista los pedidos ordenados por fecha de creación descendente",
]

def evaluate():
    results = []
    
    # ========== SQL TESTS ==========
    print("=" * 60)
    print("--- Evaluating SQL Agent (PostgreSQL) ---")
    print("=" * 60)
    for idx, query in enumerate(TEST_CASES_SQL):
        # Clasificar tipo de consulta SQL
        if idx < 4:
            query_type = "Consulta simple"
        elif idx < 8:
            query_type = "Consulta con JOIN"
        elif idx < 12:
            query_type = "Agregación"
        else:
            query_type = "Filtrado complejo"
        
        print(f"Running: {query}")
        start = time.time()
        response_dict = run_sql_agent(query)
        
        if response_dict.get("error"):
             status = "FAILED"
             error_msg = response_dict["error"]
             response_summary = error_msg if len(error_msg) < 50 else error_msg[:47] + "..."
        else:
             status = "SUCCESS"
             answer = response_dict["answer"]
             response_summary = answer if len(answer) < 50 else answer[:47] + "..."
        
        duration = time.time() - start
        results.append(["SQL", query, status, response_summary, f"{duration:.2f}s", duration, query_type])
        print(f"Result: {response_dict.get('answer', 'No answer')}\n")

    # ========== MONGODB TESTS ==========
    print("\n" + "=" * 60)
    print("--- Evaluating MongoDB Agent ---")
    print("=" * 60)
    for idx, query in enumerate(TEST_CASES_MONGO):
        # Clasificar tipo de consulta MongoDB
        if idx < 4:
            query_type = "Consulta simple"
        elif idx < 9:
            query_type = "Consulta con filtrado"
        elif idx < 13:
            query_type = "Agregación"
        else:
            query_type = "Filtrado y ordenamiento"
        
        print(f"Running: {query}")
        start = time.time()
        response_dict = run_mongo_agent(query)
        
        if response_dict.get("error"):
             status = "FAILED"
             error_msg = response_dict["error"]
             response_summary = error_msg if len(error_msg) < 50 else error_msg[:47] + "..."
        else:
             status = "SUCCESS"
             answer = response_dict["answer"]
             response_summary = answer if len(answer) < 50 else answer[:47] + "..."
        
        duration = time.time() - start
        results.append(["MongoDB", query, status, response_summary, f"{duration:.2f}s", duration, query_type])
        print(f"Result: {response_dict.get('answer', 'No answer')}\n")

    # ========== SUMMARY ==========
    print("\n" + "=" * 60)
    print("--- Final Summary (SQL + MongoDB) ---")
    print("=" * 60)
    # Mostrar tabla sin la columna de duración numérica (solo la formateada)
    display_results = [r[:5] for r in results]
    print(tabulate(display_results, headers=["Agent", "Query", "Status", "Response", "Time"], tablefmt="simple"))
    
    # Statistics
    total_tests = len(results)
    sql_tests = len([r for r in results if r[0] == "SQL"])
    mongo_tests = len([r for r in results if r[0] == "MongoDB"])
    success_tests = len([r for r in results if r[2] == "SUCCESS"])
    failed_tests = len([r for r in results if r[2] == "FAILED"])
    
    # Calcular tiempos promedio
    sql_times = [r[5] for r in results if r[0] == "SQL"]
    mongo_times = [r[5] for r in results if r[0] == "MongoDB"]
    all_times = [r[5] for r in results]
    
    sql_avg = sum(sql_times) / len(sql_times) if sql_times else 0
    mongo_avg = sum(mongo_times) / len(mongo_times) if mongo_times else 0
    total_avg = sum(all_times) / len(all_times) if all_times else 0
    
    # Tiempos por tipo de consulta
    query_types = {}
    for r in results:
        qtype = r[6]  # tipo de consulta
        if qtype not in query_types:
            query_types[qtype] = []
        query_types[qtype].append(r[5])
    
    type_averages = {qtype: sum(times)/len(times) for qtype, times in query_types.items()}
    
    print(f"\n{'=' * 60}")
    print(f"ESTADÍSTICAS:")
    print(f"  Total de tests: {total_tests}")
    print(f"  - SQL: {sql_tests}")
    print(f"  - MongoDB: {mongo_tests}")
    print(f"  Exitosos: {success_tests} ({success_tests/total_tests*100:.1f}%)")
    print(f"  Fallidos: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    print(f"\nTIEMPOS PROMEDIO:")
    print(f"  General: {total_avg:.2f}s")
    print(f"  - PostgreSQL (SQL): {sql_avg:.2f}s")
    print(f"  - MongoDB: {mongo_avg:.2f}s")
    print(f"\n  Por tipo de consulta:")
    for qtype in sorted(type_averages.keys()):
        print(f"    - {qtype}: {type_averages[qtype]:.2f}s")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    evaluate()
