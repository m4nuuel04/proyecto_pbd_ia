import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_URI = os.getenv("POSTGRES_URI")
NEW_DB_NAME = "llm_agent_db"

def recreate_database():
    try:
        # Conectar a la base de datos 'postgres' (no a llm_agent_db)
        # Reemplazar el nombre de la base de datos en la URI
        base_uri = DEFAULT_DB_URI.rsplit('/', 1)[0]
        postgres_uri = f"{base_uri}/postgres"
        
        print(f"Conectando a base de datos postgres...")
        conn = psycopg2.connect(postgres_uri)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Terminar todas las conexiones activas a la base de datos
        print(f"Terminando conexiones activas a '{NEW_DB_NAME}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{NEW_DB_NAME}'
            AND pid <> pg_backend_pid();
        """)
        
        # Eliminar la base de datos si existe
        print(f"Eliminando base de datos '{NEW_DB_NAME}' si existe...")
        cursor.execute(f"DROP DATABASE IF EXISTS {NEW_DB_NAME}")
        
        # Crear la base de datos con UTF8
        print(f"Creando base de datos '{NEW_DB_NAME}' con UTF8 encoding...")
        cursor.execute(f"""
            CREATE DATABASE {NEW_DB_NAME} 
            ENCODING 'UTF8' 
            LC_COLLATE 'C' 
            LC_CTYPE 'C' 
            TEMPLATE template0
        """)
        
        print(f"Base de datos '{NEW_DB_NAME}' recreada correctamente con UTF8")
        
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error recreando la base de datos: {repr(e)}")
        return False

if __name__ == "__main__":
    print("=== Recreando base de datos con UTF8 ===")
    if recreate_database():
        print("\nAhora ejecuta: python src/utils/setup_db.py")
        print("Para poblar la base de datos con datos de prueba")
    else:
        print("\nNo se pudo recrear la base de datos")
