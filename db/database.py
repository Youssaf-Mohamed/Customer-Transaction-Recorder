import sqlite3
from datetime import datetime

DATABASE = "modern_app.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            balance REAL DEFAULT 0
        )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            date TEXT,
            amount REAL,
            type TEXT,
            notes TEXT,
            FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
        )""")
    if len(get_customers()) == 0:
        add_initial_data()
    conn.commit()
    conn.close()


def add_initial_data():
    customers = [
        ("أحمد محمد", "0123456789", 1500.0),
        ("سارة عبدالله", "0111222333", 3000.0),
        ("علي حسن", "0100011111", 500.0)
    ]
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    for customer in customers:
        cursor.execute(
            "INSERT INTO Customers (name, phone, balance) VALUES (?, ?, ?)",
            customer
        )
    transactions = [
        (1, 500.0, "زيادة", "إيداع نقدي"),
        (1, 200.0, "خصم", "سحب من ماكينة"),
        (2, 1000.0, "زيادة", "تحويل بنكي")
    ]
    for trans in transactions:
        cursor.execute(
            """INSERT INTO Transactions
            (customer_id, date, amount, type, notes)
            VALUES (?, ?, ?, ?, ?)""",
            (trans[0], datetime.now().isoformat(),
             trans[1], trans[2], trans[3])
        )
    conn.commit()
    conn.close()


def get_customer_balance(customer_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT balance FROM Customers WHERE customer_id = ?", (customer_id,))
    balance = cursor.fetchone()[0]
    conn.close()
    return balance


def add_customer(name, phone):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Customers (name, phone) VALUES (?, ?)", (name, phone))
    conn.commit()
    conn.close()


def update_customer_info(customer_id, name, phone):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Customers SET name = ?, phone = ? WHERE customer_id = ?", (name, phone, customer_id))
    conn.commit()
    conn.close()


def add_transaction(customer_id, amount, trans_type, notes):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO Transactions
        (customer_id, date, amount, type, notes)
        VALUES (?, ?, ?, ?, ?)""",
        (customer_id, datetime.now().isoformat(), amount, trans_type, notes)
    )
    if trans_type == "زيادة":
        cursor.execute(
            "UPDATE Customers SET balance = balance + ? WHERE customer_id = ?", (amount, customer_id))
    else:
        cursor.execute(
            "UPDATE Customers SET balance = balance - ? WHERE customer_id = ?", (amount, customer_id))
    conn.commit()
    conn.close()


def get_customers():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    conn.close()
    return customers


def get_customer(customer_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM Customers WHERE customer_id = ?", (customer_id,))
    customer = cursor.fetchone()
    conn.close()
    return customer


def get_transactions(customer_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            transaction_id,
            customer_id,
            date,
            amount,
            type,
            notes
        FROM Transactions
        WHERE customer_id = ?
        ORDER BY date DESC""", (customer_id,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions


def get_total_balance():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(balance) FROM Customers")
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total
