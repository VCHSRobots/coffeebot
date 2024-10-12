import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='coffeebot.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS coffee_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            battery_level REAL,
            is_live BOOLEAN,
            total_runs INTEGER,
            daily_runs INTEGER
        )
        ''')
        self.conn.commit()

    def insert_data(self, battery_level, is_live, total_runs, daily_runs):
        self.cursor.execute('''
        INSERT INTO coffee_runs (timestamp, battery_level, is_live, total_runs, daily_runs)
        VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now(), battery_level, is_live, total_runs, daily_runs))
        self.conn.commit()

    def get_latest_data(self):
        self.cursor.execute('''
        SELECT * FROM coffee_runs ORDER BY timestamp DESC LIMIT 1
        ''')
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()
