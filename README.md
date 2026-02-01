# Retail-Buddy

**Retail-Buddy** is a modern, lightweight ERP solution designed for small to medium-sized retail businesses. It allows you to manage inventory, customers, categories, suppliers, and sales orders with a sleek, user-friendly interface.

## Features

- **Inventory Management**: Add, update, and track products with stock levels.
- **Customer Management**: Maintain a database of customers with their contact info.
- **Supplier & Category Management**: Organize products effectively.
- **Order Processing**: Create sales orders and track revenue.
- **Dashboard**: Real-time overview of sales, low stock items, and recent activity.
- **User Authentication**: Secure signup and login for multi-user support (Data is isolated per user).

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS (Custom Design, responsive)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd retail-buddy
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the Database:**
    The application uses SQLite. You can initialize the database schema by running:
    ```bash
    python init_db.py
    ```
    *(Note: The app will also automatically attempt to connect to `bizflow.db`. Ensure `init_db.py` creates the necessary tables.)*

5.  **Run the Application:**
    ```bash
    python app.py
    ```

6.  **Access the App:**
    Open your browser and navigate to `http://127.0.0.1:8000`.

## Usage

- **Sign Up**: Create a new account to get your own isolated workspace.
- **Dashboard**: View your key metrics.
- **Products**: Add your inventory items.
- **Orders**: Create new sales orders for customers.

## License

MIT License.
