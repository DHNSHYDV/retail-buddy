from flask import Flask, render_template, request, redirect, url_for, g, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'dev-secret-key' # Change this for production!
DB_FILE = "bizflow.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_FILE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Auth Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        
        error = "Invalid username or password"
        return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            hashed_pw = generate_password_hash(password)
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                           (username, hashed_pw))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Username already taken."
            return render_template('signup.html', error=error)
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- App Routes ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    # 1. Total Revenue (Filtered by User)
    cursor.execute("SELECT SUM(total_amount) as total FROM orders WHERE user_id = ? AND status != 'Cancelled'", (user_id,))
    revenue_row = cursor.fetchone()
    total_revenue = revenue_row['total'] if revenue_row['total'] else 0

    # 2. Total Orders (Filtered by User)
    cursor.execute("SELECT COUNT(*) as count FROM orders WHERE user_id = ?", (user_id,))
    total_orders = cursor.fetchone()['count']

    # 3. Low Stock Items (Filtered by User)
    cursor.execute("SELECT * FROM products WHERE user_id = ? AND stock_quantity < 20", (user_id,))
    low_stock_items = cursor.fetchall()
    low_stock_count = len(low_stock_items)

    # 4. Recent Orders (Filtered by User)
    cursor.execute("""
        SELECT o.id, c.name as customer_name, o.total_amount, o.status, o.order_date
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.user_id = ?
        ORDER BY o.order_date DESC
        LIMIT 5
    """, (user_id,))
    recent_orders = cursor.fetchall()

    return render_template('dashboard.html', 
                           revenue=total_revenue, 
                           orders_count=total_orders,
                           low_stock_count=low_stock_count,
                           low_stock_items=low_stock_items,
                           recent_orders=recent_orders)

@app.route('/products')
@login_required
def products():
    conn = get_db()
    cursor = conn.cursor()
    # Filter products by User
    cursor.execute("""
        SELECT p.*, c.name as category_name, s.name as supplier_name 
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN suppliers s ON p.supplier_id = s.id
        WHERE p.user_id = ?
    """, (session['user_id'],))
    products = cursor.fetchall()
    return render_template('products.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    if request.method == 'POST':
        name = request.form['name']
        sku = request.form['sku']
        price = float(request.form['price'])
        stock = int(request.form['stock_quantity'])
        category_id = request.form['category_id'] or None
        supplier_id = request.form['supplier_id'] or None
        description = request.form['description']

        try:
            cursor.execute("""
                INSERT INTO products (user_id, name, sku, price, stock_quantity, description, category_id, supplier_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, sku, price, stock, description, category_id, supplier_id))
            conn.commit()
            return redirect(url_for('products'))
        except sqlite3.Error as e:
            # Handle potential SKU uniqueness error if we enforced it, or generic errors
            error = f"Database Error: {e}"
    
    # GET request or Error: Fetch categories and suppliers for dropdowns
    cursor.execute("SELECT id, name FROM categories WHERE user_id = ?", (user_id,))
    categories = cursor.fetchall()
    
    cursor.execute("SELECT id, name FROM suppliers WHERE user_id = ?", (user_id,))
    suppliers = cursor.fetchall()

    return render_template('add_product.html', categories=categories, suppliers=suppliers, error=locals().get('error'))

@app.route('/customers')
@login_required
def customers():
    conn = get_db()
    cursor = conn.cursor()
    # Filter customers by User
    cursor.execute("SELECT * FROM customers WHERE user_id = ?", (session['user_id'],))
    customers = cursor.fetchall()

    return render_template('customers.html', customers=customers)

@app.route('/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        status = request.form['status']

        try:
            cursor.execute("""
                INSERT INTO customers (user_id, name, email, phone, status)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, email, phone, status))
            conn.commit()
            return redirect(url_for('customers'))
        except sqlite3.Error as e:
            error = f"Database Error: {e}"
            return render_template('add_customer.html', error=error)
            
    return render_template('add_customer.html')

@app.route('/orders')
@login_required
def orders():
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']
    
    # Fetch orders for this User only
    cursor.execute("""
        SELECT o.id, c.name as customer_name, o.total_amount, o.status, o.order_date
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.user_id = ?
        ORDER BY o.order_date DESC
    """, (user_id,))
    orders = cursor.fetchall()
    
    # Fetch data for the form (User's customers/products only)
    cursor.execute("SELECT id, name FROM customers WHERE user_id = ?", (user_id,))
    customers_list = cursor.fetchall()
    
    cursor.execute("SELECT id, name, price, stock_quantity FROM products WHERE user_id = ? AND stock_quantity > 0", (user_id,))
    products_list = cursor.fetchall()
    
    return render_template('orders.html', orders=orders, customers=customers_list, products=products_list)

@app.route('/create_order', methods=['POST'])
@login_required
def create_order():
    customer_id = request.form.get('customer_id')
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity'))
    user_id = session['user_id']
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # 1. Get Product Price and Check Stock (Ensure Product belongs to User!)
        cursor.execute("SELECT price, stock_quantity FROM products WHERE id = ? AND user_id = ?", (product_id, user_id))
        product = cursor.fetchone()
        
        if not product:
            return "Error: Product not found or access denied."
            
        if product['stock_quantity'] < quantity:
            return "Error: Not enough stock!"
            
        unit_price = product['price']
        total_amount = unit_price * quantity
        
        # 2. Create Order (Tag with User ID)
        cursor.execute("INSERT INTO orders (user_id, customer_id, total_amount, status) VALUES (?, ?, ?, 'Completed')", 
                       (user_id, customer_id, total_amount))
        order_id = cursor.lastrowid
        
        # 3. Create Order Item
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                       (order_id, product_id, quantity, unit_price))
                       
        # 4. Update Stock
        cursor.execute("UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?", 
                       (quantity, product_id))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        return f"An error occurred: {e}"
        
    return redirect(url_for('orders'))

    return redirect(url_for('orders'))

@app.route('/management')
@login_required
def management():
    conn = get_db()
    cursor = conn.cursor()
    user_id = session['user_id']
    
    cursor.execute("SELECT * FROM categories WHERE user_id = ?", (user_id,))
    categories = cursor.fetchall()
    
    cursor.execute("SELECT * FROM suppliers WHERE user_id = ?", (user_id,))
    suppliers = cursor.fetchall()
    
    return render_template('management.html', categories=categories, suppliers=suppliers)

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form['name']
    user_id = session['user_id']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    
    return redirect(url_for('management'))

@app.route('/add_supplier', methods=['POST'])
@login_required
def add_supplier():
    name = request.form['name']
    user_id = session['user_id']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO suppliers (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    
    return redirect(url_for('management'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)
