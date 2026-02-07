import sqlite3
from werkzeug.security import generate_password_hash

DB = "voting.db"

def connect():
    return sqlite3.connect(DB)

def init_db():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        voted INTEGER DEFAULT 0,
        role TEXT DEFAULT 'user'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        votes INTEGER DEFAULT 0
    )
    """)

    # Create admin automatically
    cur.execute("SELECT * FROM users WHERE role='admin'")
    if not cur.fetchone():
        cur.execute("""
        INSERT INTO users(username,password,role)
        VALUES(?,?,?)
        """, ("admin", generate_password_hash("admin123"), "admin"))

    con.commit()
    con.close()
