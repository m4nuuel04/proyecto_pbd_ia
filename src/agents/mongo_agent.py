from langchain_ollama import ChatOllama
import os
import re
from pymongo import MongoClient
import json
from src.utils.encoding_utils import safe_load_dotenv
from bson import json_util

safe_load_dotenv()

def run_mongo_agent(query: str):
    """
    Executes a natural language query against MongoDB using a deterministic
    generate-execute-interpret pipeline.
    """
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")
    
    if not mongo_uri or not db_name:
        return {"error": "Error: MONGO_URI or MONGO_DB_NAME environment variable not set."}
    
    client = None
    try:
        # 1. Setup
        client = MongoClient(mongo_uri)
        db = client[db_name]
        llm = ChatOllama(model="llama3", temperature=0)
        
        # 2. Get Schema (Inferred from collections and first document)
        collections = db.list_collection_names()
        schema_info = {}
        for col_name in collections:
            doc = db[col_name].find_one()
            if doc:
                # Convert ObjectIds and Datetimes to string for schema representation
                doc_str = json.dumps(json.loads(json_util.dumps(doc)), indent=2)
                schema_info[col_name] = doc_str
            else:
                schema_info[col_name] = "Empty Collection"
        
        schema_context = json.dumps(schema_info, indent=2)

        # 3. Generate PyMongo Code (Explicit Chain Step 1)
        # We ask for Python code using pymongo because MQL is harder to execute directly purely as a string in some contexts,
        # but generating a python script to execute is risky.
        # Safer approach: Generate a "mongo shell" style query or specific finding parameters.
        # Let's try generating a Python block that defines a result variable.
        
        generation_prompt = (
            f"Tu tarea es generar código PYTHON usando `pymongo` para consultar MongoDB basado en la pregunta del usuario y el esquema (ejemplo de documentos).\n"
            f"ESQUEMA (Colecciones y un documento de ejemplo):\n{schema_context}\n\n"
            f"PREGUNTA: {query}\n\n"
            "INSTRUCCIONES:\n"
            "1. Responde SOLAMENTE con código Python dentro de un bloque markdown ```python ... ```.\n"
            "2. Asume que existe una variable `db` que ya es la conexión a la base de datos.\n"
            "3. El código debe ejecutar la consulta y guardar el resultado en una variable llamada `result`.\n"
            "4. `result` debe ser una lista de diccionarios (usa `list(cursor)` si es necesario) o un valor simple (count).\n"
            "5. NO uses ObjectId() ni formato JSON extendido de MongoDB como {{'$oid': '...'}}.\n"
            "6. Para buscar por campos de texto, usa directamente strings: {{'nombre': 'Bob'}}\n"
            "7. Para buscar por _id (si es necesario), usa from bson import ObjectId y ObjectId('id_string').\n"
            "8. NO importes pymongo ni MongoClient, solo usa `db` directamente.\n"
            "9. Ejemplos válidos:\n"
            "   - result = list(db.users.find({{'name': 'Alice'}}))\n"
            "   - result = list(db.orders.find({{'user_name': 'Bob'}}))\n"
            "   - result = db.users.count_documents({{}})\n"
        )
        
        response_gen = llm.invoke(generation_prompt)
        content_gen = response_gen.content if hasattr(response_gen, 'content') else str(response_gen)
        
        # Extract Code
        generated_code = ""
        code_match = re.search(r"```python\s*(.*?)```", content_gen, re.IGNORECASE | re.DOTALL)
        
        if code_match:
            generated_code = code_match.group(1).strip()
        else:
             # Fallback: try to find lines that start with result = 
            if "result =" in content_gen:
                generated_code = content_gen.strip()
            else:
                return {
                    "answer": "No pude generar código PyMongo válido.",
                    "sql_queries": [], # reusing key for consistency for now, or rename to generated_code
                    "raw_results": [],
                    "error": "Code Extraction Failed"
                }

        # 4. Execute Code (Explicit Step 2)
        # WARNING: Executing generated code is dangerous. In a real prod env, this needs strict sandboxing.
        # For this prototype local CLI, we use exec with restricted locals.
        # Import ObjectId in case the generated code needs it
        from bson import ObjectId
        local_scope = {'db': db, 'ObjectId': ObjectId}
        try:
            exec(generated_code, {}, local_scope)
            raw_result = local_scope.get('result', "No result variable found")
        except Exception as e:
            return {
                "answer": f"Error al ejecutar el código MongoDB: {str(e)}",
                "sql_queries": [generated_code],
                "raw_results": [f"Error: {str(e)}"],
                "error": str(e)
            }
            
        # Serialize raw_result for display/prompt
        raw_result_str = json_util.dumps(raw_result)

        # 5. Interpret Result (Explicit Step 3)
        interpretation_prompt = (
            f"Pregunta Original: {query}\n"
            f"Código Ejecutado: {generated_code}\n"
            f"Resultado de la Base de Datos: {raw_result_str}\n\n"
            "INSTRUCCIONES:\n"
            "1. Responde a la pregunta original basándote en el resultado.\n"
            "2. Responde en ESPAÑOL.\n"
            "3. Explica DETALLADAMENTE los resultados.\n"
        )
        
        response_int = llm.invoke(interpretation_prompt)
        final_answer = response_int.content if hasattr(response_int, 'content') else str(response_int)

        return {
            "answer": final_answer,
            "sql_queries": [generated_code], # showing code instead of SQL
            "raw_results": [raw_result_str],
            "error": None
        }

    except Exception as e:
        return {
            "answer": "Ocurrió un error inesperado en el agente Mongo.",
            "sql_queries": [],
            "raw_results": [],
            "error": str(e)
        }
    finally:
        if client:
            client.close()
