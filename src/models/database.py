import sqlite3
import os
from pathlib import Path

class Database:
    def __init__(self):
        self.db_path = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / 'keycrate.db'
        self.connection = None
        self.cursor = None
        self.setup()

    def connect(self):
        self.connection = sqlite3.connect(str(self.db_path))
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def setup(self):
        self.connect()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password BLOB NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                account_name TEXT NOT NULL,
                password BLOB NOT NULL,
                url TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        self.connection.commit()
        self.disconnect()
