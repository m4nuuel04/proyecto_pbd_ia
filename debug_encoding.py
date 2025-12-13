"""
Script de depuración para encontrar el problema de encoding
"""
import traceback
import sys
import os
from src.utils.encoding_utils import safe_load_dotenv

# Fix for psycopg2 encoding issues on Windows
# Disable reading of potentially corrupted config files  
os.environ['PGPASSFILE'] = 'nul'  # Windows null device
os.environ['PGSERVICEFILE'] = 'nul'
os.environ['PGSYSCONFDIR'] = 'nul'

print("=" * 60)
print("DEBUGGING ENCODING ISSUE (with PG config files disabled)")
print("=" * 60)

# Load environment
print("\n1. Loading .env file...")
safe_load_dotenv(verbose=True)
print(f"   POSTGRES_URI: {os.getenv('POSTGRES_URI')[:50]}...")

# Try importing modules
print("\n2. Importing modules...")
try:
    from langchain_community.utilities import SQLDatabase
    print("   [OK] SQLDatabase imported")
except Exception as e:
    print(f"   [ERROR] Error importing SQLDatabase: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from langchain_ollama import ChatOllama
    print("   [OK] ChatOllama imported")
except Exception as e:
    print(f"   [ERROR] Error importing ChatOllama: {e}")
    traceback.print_exc()
    sys.exit(1)

# Try connecting to database
print("\n3. Connecting to PostgreSQL...")
db_uri = os.getenv("POSTGRES_URI")
try:
    # Try with encoding parameter
    if "?" in db_uri:
        db_uri_fixed = f"{db_uri}&client_encoding=utf8"
    else:
        db_uri_fixed = f"{db_uri}?client_encoding=utf8"
    
    print(f"   URI: {db_uri_fixed[:70]}...")
    db = SQLDatabase.from_uri(db_uri_fixed, sample_rows_in_table_info=0)
    print("   [OK] Database connected successfully")
except Exception as e:
    print(f"   [ERROR] Error connecting to database: {e}")
    print("\n   FULL TRACEBACK:")
    traceback.print_exc()
    
    # Try to get more details
    print("\n   Trying to connect with SQLAlchemy directly...")
    try:
        from sqlalchemy import create_engine
        engine = create_engine(db_uri_fixed)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("   [OK] SQLAlchemy direct connection works")
    except Exception as e2:
        print(f"   [ERROR] SQLAlchemy also fails: {e2}")
        traceback.print_exc()
    
    sys.exit(1)

# Try getting table info
print("\n4. Getting table information...")
try:
    table_info = db.get_table_info()
    print(f"   [OK] Got table info ({len(table_info)} chars)")
    print(f"\n   First 200 chars:\n   {table_info[:200]}")
except Exception as e:
    print(f"   [ERROR] Error getting table info: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("SUCCESS - No encoding errors detected!")
print("=" * 60)
