from langchain_community.utilities import SQLDatabase
from langchain_ollama import ChatOllama
import os
import re
from src.utils.encoding_utils import safe_load_dotenv

safe_load_dotenv()

def run_sql_agent(query: str):
    """
    Executes a natural language query against PostgreSQL using a deterministic
    generate-execute-interpret pipeline instead of an Agent loop.
    """
    db_uri = os.getenv("POSTGRES_URI")
    if not db_uri:
        return {"error": "Error: POSTGRES_URI environment variable not set."}
    
    try:
        # 1. Setup
        # Force sample_rows=0 to avoid privacy leaks / overhead, just getting schema
        db = SQLDatabase.from_uri(db_uri, sample_rows_in_table_info=0)
        llm = ChatOllama(model="llama3", temperature=0)
        
        # 2. Get Schema
        table_context = db.get_table_info()
        
        # 3. Generate SQL (Explicit Chain Step 1)
        generation_prompt = (
            f"Tu tarea es generar una consulta SQL para PostgreSQL basada en la pregunta del usuario y el esquema proporcionado.\n"
            f"ESQUEMA:\n{table_context}\n\n"
            f"PREGUNTA: {query}\n\n"
            "INSTRUCCIONES:\n"
            "1. Responde SOLAMENTE con el código SQL dentro de un bloque markdown ```sql ... ```.\n"
            "2. No des explicaciones, solo el SQL.\n"
            "3. Para uniones (JOIN), usa las claves foráneas correctas (ej: users.id = orders.user_id).\n"
            "4. Para calcular dinero total, suma 'total_amount' en la tabla 'orders'.\n"
        )
        
        response_gen = llm.invoke(generation_prompt)
        content_gen = response_gen.content if hasattr(response_gen, 'content') else str(response_gen)
        
        # Extract SQL using Regex
        generated_sql = ""
        sql_match = re.search(r"```sql\s*(SELECT.*?)```", content_gen, re.IGNORECASE | re.DOTALL)
        if not sql_match:
            # Fallback regex
            sql_match = re.search(r"(SELECT\s.*?\sFROM\s.*?(?:;|$))", content_gen, re.IGNORECASE | re.DOTALL)
            
        if sql_match:
            generated_sql = sql_match.group(1).strip()
        else:
            return {
                "answer": "No pude generar una consulta SQL válida para tu pregunta.",
                "sql_queries": [],
                "raw_results": [],
                "error": "SQL Extraction Failed"
            }

        # 4. Execute SQL (Explicit Step 2)
        try:
            raw_result = db.run(generated_sql)
        except Exception as e:
            return {
                "answer": f"Error al ejecutar la consulta SQL: {str(e)}",
                "sql_queries": [generated_sql],
                "raw_results": [f"Error: {str(e)}"],
                "error": str(e)
            }

        # 5. Interpret Result (Explicit Step 3)
        interpretation_prompt = (
            f"Pregunta Original: {query}\n"
            f"Consulta SQL: {generated_sql}\n"
            f"Resultado de la Base de Datos: {raw_result}\n\n"
            "INSTRUCCIONES:\n"
            "1. Responde a la pregunta original basándote en el resultado.\n"
            "2. Responde en ESPAÑOL.\n"
            "3. Explica DETALLADAMENTE los resultados. No hagas resúmenes breves. Si hay lista de datos, menciona los detalles importantes de cada uno.\n"
        )
        
        response_int = llm.invoke(interpretation_prompt)
        final_answer = response_int.content if hasattr(response_int, 'content') else str(response_int)

        return {
            "answer": final_answer,
            "sql_queries": [generated_sql],
            "raw_results": [str(raw_result)],
            "error": None
        }

    except Exception as e:
        return {
            "answer": "Ocurrió un error inesperado.",
            "sql_queries": [],
            "raw_results": [],
            "error": str(e)
        }
