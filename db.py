import sqlite3
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    serving_size: float
    calories: float
    protein: float


class DB:
    def __init__(self, db_file):
        self._conn = sqlite3.connect(db_file)

        cursor = self._conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS items
        (
            name        VARCHAR(255) NOT NULL UNIQUE,
            servingSize FLOAT NOT NULL,
            calories    FLOAT NOT NULL,
            protein     FLOAT NOT NULL
        )
        ''')

        self._conn.commit()


    def __del__(self):
        self._conn.close()


    def get_items(self):
        cursor = self._conn.cursor()

        res = cursor.execute('SELECT * FROM items')

        return res.fetchall()


    def insert_item(self, item: Item):
        cursor = self._conn.cursor()

        cursor.execute('INSERT INTO items VALUES (?, ?, ?, ?)',
                       (item.name, item.serving_size, item.calories, item.protein))

        self._conn.commit()


    def remove_items(self, item_names: list[str]):
        cursor = self._conn.cursor()

        seq_of_parameters = [(name,) for name in item_names]

        cursor.executemany('DELETE FROM items WHERE name = ?',
                           seq_of_parameters)

        self._conn.commit()