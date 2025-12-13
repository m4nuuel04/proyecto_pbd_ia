import sys
import os

# Ensure the root directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.sql_agent import run_sql_agent
from tabulate import tabulate
import time

# Define test cases. 
TEST_CASES_SQL = [
    "List all tables in the database.",
    "Count the total number of records in the most populated table.",
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
             response_summary = response_dict["error"]
        else:
             status = "SUCCESS"
             answer = response_dict["answer"]
             response_summary = answer if len(answer) < 100 else answer[:97] + "..."
        
        duration = time.time() - start
        results.append(["SQL", query, status, response_summary, f"{duration:.2f}s"])
        print(f"Result: {response_dict.get('answer', 'No answer')}\n")

    print("\n--- Final Summary ---")
    print(tabulate(results, headers=["Agent", "Query", "Status", "Response Summary", "Time"], tablefmt="grid"))

if __name__ == "__main__":
    evaluate()
