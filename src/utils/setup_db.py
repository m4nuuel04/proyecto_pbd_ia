import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta
import pymongo # Added for MongoDB

load_dotenv()

# Configuration
DEFAULT_DB_URI = os.getenv("POSTGRES_URI")
NEW_DB_NAME = "llm_agent_db"

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "llm_agent_db")


def create_postgres_database():
    try:
        conn = psycopg2.connect(DEFAULT_DB_URI)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{NEW_DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating Postgres database '{NEW_DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {NEW_DB_NAME}")
        else:
            print(f"Postgres database '{NEW_DB_NAME}' already exists.")
            
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating Postgres database: {repr(e)}")
        return False

def populate_postgres():
    try:
        base_uri = DEFAULT_DB_URI.rsplit('/', 1)[0]
        new_db_uri = f"{base_uri}/{NEW_DB_NAME}"
        
        print(f"Connecting to Postgres '{NEW_DB_NAME}' to expand schema...")
        conn = psycopg2.connect(new_db_uri)
        cursor = conn.cursor()
        
        # 1. Drop old tables (Reset)
        cursor.execute("""
            DROP TABLE IF EXISTS orders CASCADE;
            DROP TABLE IF EXISTS products CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
        """)
        
        # 2. Create Expanded Schema
        tables_sql = """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INTEGER,
            city VARCHAR(50),
            country VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            category VARCHAR(50),
            stock INTEGER DEFAULT 0,
            rating DECIMAL(3, 2),
            description TEXT
        );

        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) CHECK (status IN ('Pending', 'Shipped', 'Delivered', 'Cancelled')),
            payment_method VARCHAR(50),
            total_amount DECIMAL(10, 2)
        );
        """
        cursor.execute(tables_sql)
        print("Postgres Schema created.")

        # 3. Seed Users (10 users)
        users = [
            ('alice', 'alice@example.com', 28, 'Madrid', 'Spain'),
            ('bob', 'bob@example.com', 35, 'Barcelona', 'Spain'),
            ('charlie', 'charlie@example.com', 22, 'Paris', 'France'),
            ('david', 'david@example.com', 40, 'Berlin', 'Germany'),
            ('eve', 'eve@example.com', 30, 'London', 'UK'),
            ('frank', 'frank@example.com', 55, 'New York', 'USA'),
            ('grace', 'grace@example.com', 29, 'Toronto', 'Canada'),
            ('heidi', 'heidi@example.com', 45, 'Madrid', 'Spain'),
            ('ivan', 'ivan@example.com', 32, 'Moscow', 'Russia'),
            ('judy', 'judy@example.com', 27, 'Valencia', 'Spain')
        ]
        
        cursor.executemany(
            "INSERT INTO users (username, email, age, city, country) VALUES (%s, %s, %s, %s, %s)",
            users
        )
        print(f"Seeded {len(users)} users to Postgres.")

        # 4. Seed Products (15 products)
        products = [
            ('Laptop Pro', 1200.00, 'Electronics', 50, 4.8, 'High performance laptop'),
            ('Smartphone X', 800.00, 'Electronics', 100, 4.5, 'Latest flagship phone'),
            ('Wireless Headphones', 150.00, 'Electronics', 200, 4.2, 'Noise cancelling'),
            ('4K Monitor', 300.00, 'Electronics', 30, 4.6, '32 inch display'),
            ('Gaming Mouse', 50.00, 'Electronics', 150, 4.0, 'RGB mouse'),
            ('Office Chair', 250.00, 'Furniture', 20, 4.7, 'Ergonomic chair'),
            ('Standing Desk', 400.00, 'Furniture', 15, 4.8, 'Motorized desk'),
            ('Bookshelf', 120.00, 'Furniture', 40, 4.1, 'Wooden 5-tier shelf'),
            ('Sofa', 600.00, 'Furniture', 10, 4.3, 'Comfortable 3-seater'),
            ('Cotton T-Shirt', 25.00, 'Clothing', 500, 4.2, '100% Cotton'),
            ('Jeans', 60.00, 'Clothing', 300, 4.4, 'Slim fit'),
            ('Sneakers', 90.00, 'Clothing', 120, 4.5, 'Running shoes'),
            ('Blender', 45.0, 'Home', 80, 4.0, 'High speed blender'),
            ('Coffee Maker', 85.00, 'Home', 60, 4.6, 'Programmable'),
            ('Air Fryer', 110.00, 'Home', 45, 4.8, 'Digital air fryer')
        ]
        
        cursor.executemany(
            "INSERT INTO products (name, price, category, stock, rating, description) VALUES (%s, %s, %s, %s, %s, %s)",
            products
        )
        print(f"Seeded {len(products)} products to Postgres.")

        # 5. Seed Orders (Randomized)
        status_list = ['Pending', 'Shipped', 'Delivered', 'Cancelled']
        payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Bitcoin']
        
        orders_data = []
        for _ in range(50): # 50 Random orders
            user_id = random.randint(1, 10)
            
            # Simple logic: Pick a random product price * random quantity (1-3)
            prod_price = random.choice(products)[1]
            total_amount = round(prod_price * random.randint(1, 3), 2)
            
            status = random.choice(status_list)
            payment = random.choice(payment_methods)
            date = datetime.now() - timedelta(days=random.randint(0, 365))
            
            orders_data.append((user_id, date, status, payment, total_amount))
            
        cursor.executemany(
            "INSERT INTO orders (user_id, order_date, status, payment_method, total_amount) VALUES (%s, %s, %s, %s, %s)",
            orders_data
        )
        print(f"Seeded {len(orders_data)} orders to Postgres.")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Postgres population complete!")
        return True
    except Exception as e:
        print(f"Error executing Postgres SQL script: {e}")
        return False

def populate_mongo():
    print("\n--- Populating MongoDB ---")
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        
        # Clear existing collections
        db.users.drop()
        db.orders.drop()
        print("Existing collections 'users' and 'orders' dropped.")

        # Sample Data: Users
        users_data = [
            {"name": "Alice Smith", "email": "alice@example.com", "created_at": datetime.now()},
            {"name": "Bob Jones", "email": "bob@example.com", "created_at": datetime.now()},
            {"name": "Charlie Brown", "email": "charlie@example.com", "created_at": datetime.now()},
            {"name": "Diana Prince", "email": "diana@example.com", "created_at": datetime.now()},
            {"name": "Evan Wright", "email": "evan@example.com", "created_at": datetime.now()},
        ]
        
        users_result = db.users.insert_many(users_data)
        user_ids = users_result.inserted_ids
        print(f"Inserted {len(user_ids)} users to Mongo.")

        # Sample Data: Orders
        orders_data = []
        statuses = ["pending", "completed", "shipped", "cancelled"]
        
        for i in range(15):
            user_id = random.choice(user_ids)
            order = {
                "user_id": user_id,
                "total_amount": round(random.uniform(20.0, 500.0), 2),
                "status": random.choice(statuses),
                "created_at": datetime.now()
            }
            orders_data.append(order)
            
        db.orders.insert_many(orders_data)
        print(f"Inserted {len(orders_data)} orders to Mongo.")
        
        print("MongoDB population complete!")
        client.close()
        return True
    except Exception as e:
        print(f"Error populating MongoDB: {e}")
        return False

if __name__ == "__main__":
    print("Starting Unified Database Setup...\n")
    
    # Postgres
    if create_postgres_database():
        populate_postgres()
        
    # MongoDB
    populate_mongo()
    
    print("\nAll database setup steps finished.")
