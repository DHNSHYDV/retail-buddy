import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_FILE = "bizflow.db"
SCHEMA_FILE = "schema.sql"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(SCHEMA_FILE, 'r') as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    print("✅ Database initialized and tables recreated.")

    print("🌱 Seeding data for Multi-Tenancy...")

    # --- USER 1: Admin (Tech Store) ---
    pw_hash = generate_password_hash('password123')
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ('admin', pw_hash))
    user1_id = cursor.lastrowid

    # --- USER 2: CoffeeShop (Cafe) ---
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ('cafe_owner', pw_hash))
    user2_id = cursor.lastrowid

    # --- DATA FOR USER 1 (Tech Store) ---
    # Categories
    cursor.execute("INSERT INTO categories (user_id, name, description) VALUES (?, ?, ?)", (user1_id, 'Electronics', 'Gadgets'))
    cat1_id = cursor.lastrowid
    
    # Suppliers
    cursor.execute("INSERT INTO suppliers (user_id, name) VALUES (?, ?)", (user1_id, 'Tech Supplier Inc'))
    sup1_id = cursor.lastrowid

    # Products
    products_u1 = [
        (user1_id, 'Wireless Mouse', 'TECH-001', 25.00, 100, cat1_id, sup1_id),
        (user1_id, 'Gaming Laptop', 'TECH-002', 1200.00, 10, cat1_id, sup1_id)
    ]
    cursor.executemany("INSERT INTO products (user_id, name, sku, price, stock_quantity, category_id, supplier_id) VALUES (?, ?, ?, ?, ?, ?, ?)", products_u1)
    
    # Customers
    cursor.execute("INSERT INTO customers (user_id, name, email, status) VALUES (?, ?, ?, ?)", (user1_id, 'Tech Buyer', 'buyer@tech.com', 'VIP'))
    cust1_id = cursor.lastrowid

    # Order
    cursor.execute("INSERT INTO orders (user_id, customer_id, total_amount, status) VALUES (?, ?, 25.00, 'Completed')", (user1_id, cust1_id))


    # --- DATA FOR USER 2 (Cafe) ---
    # Categories
    cursor.execute("INSERT INTO categories (user_id, name, description) VALUES (?, ?, ?)", (user2_id, 'Beverages', 'Hot and Cold Drinks'))
    cat2_id = cursor.lastrowid
    
    # Suppliers
    cursor.execute("INSERT INTO suppliers (user_id, name) VALUES (?, ?)", (user2_id, 'Coffee Beans Co'))
    sup2_id = cursor.lastrowid

    # Products
    products_u2 = [
        (user2_id, 'Espresso Shot', 'CAF-001', 3.50, 500, cat2_id, sup2_id),
        (user2_id, 'Croissant', 'CAF-FOOD-001', 4.00, 50, cat2_id, sup2_id)
    ]
    cursor.executemany("INSERT INTO products (user_id, name, sku, price, stock_quantity, category_id, supplier_id) VALUES (?, ?, ?, ?, ?, ?, ?)", products_u2)
    
    # Customers
    cursor.execute("INSERT INTO customers (user_id, name, email, status) VALUES (?, ?, ?, ?)", (user2_id, 'Daily Regular', 'coffee@lover.com', 'Active'))


    conn.commit()
    conn.close()
    print("🎉 Seeded data for 'admin' (Tech Store) and 'cafe_owner' (Coffee Shop).")

if __name__ == "__main__":
    init_db()
