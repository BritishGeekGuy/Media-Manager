import sqlite3

def db_connect():
    conn = sqlite3.connect('data/database.db')
    conn.execute('PRAGMA foreign_keys = ON')
    return conn
