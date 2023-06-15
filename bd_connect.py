import sqlite3

# Підключення до бази даних SQLite
conn = sqlite3.connect('usersID.db')
cursor = conn.cursor()

# Створення таблиці з користувачами, якщо вона не існує
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        fullname TEXT
    )
''')
# Створення таблиці з чорним списком користувачів, якщо вона не існує
cursor.execute('''
    CREATE TABLE IF NOT EXISTS blacklist (
        id INTEGER PRIMARY KEY
    )
''')