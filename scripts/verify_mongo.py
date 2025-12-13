import os
import sys
from dotenv import load_dotenv

def check_mongo():
    print("Verificando entorno MongoDB...")
    
    # Check pymongo
    try:
        import pymongo
        print(f"[OK] pymongo instalado: v{pymongo.version}")
    except ImportError:
        print("[FAIL] pymongo no encontrado. Ejecuta: pip install -r requirements.txt")
        return

    # Check connection
    load_dotenv()
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    print(f"Intentando conectar a: {uri}")
    
    try:
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.server_info() # Trigger connection
        print("[OK] Conexion exitosa a MongoDB")
    except Exception as e:
        print(f"[WARN] No se pudo conectar a MongoDB: {e}")
        print("Asegurate de que Mongo este corriendo o configura MONGO_URI en .env")

if __name__ == "__main__":
    check_mongo()
