import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')


class DatabaseManager:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connect(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    def execute_query(self, query, params=None):
        conn = self.connect()
        cur = conn.cursor()
        try:
            cur.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cur.fetchall()
                return result
            else:
                conn.commit()
                print('Query executed successfully')
        except Exception as e:
            print(f'Error executing query: {e}')
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def create_tables(self):
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS authorized_users (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(255) NOT NULL UNIQUE,
            user_id BIGINT NOT NULL,
            trader_id VARCHAR(255) NOT NULL,
            is_authenticated BOOLEAN DEFAULT FALSE,
            CONSTRAINT unique_phone_user UNIQUE (phone_number, user_id)
        );
        """)
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS config (
            id SERIAL PRIMARY KEY,
            key VARCHAR(255) NOT NULL UNIQUE,
            value TEXT NOT NULL
        );
        """)


db_manager = DatabaseManager(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
