import sqlite3
from datetime import date
from models import Item, Record


class DB:
    def __init__(self, db_file):
        self._conn = sqlite3.connect(db_file)

        cursor = self._conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS items
        (
            name        VARCHAR(255),
            servingSize FLOAT NOT NULL,
            calories    FLOAT NOT NULL,
            protein     FLOAT NOT NULL,
            PRIMARY KEY (name)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS records
        (
            date   DATE NOT NULL,
            food   VARCHAR(255) NOT NULL,
            amount FLOAT NOT NULL,
            FOREIGN KEY (food) REFERENCES items (name)
                ON DELETE RESTRICT
        )
        ''')

        self._conn.commit()


    def __del__(self):
        self._conn.close()


    def get_joined_records(self, search_date: date):
        cursor = self._conn.cursor()

        query = '''
        SELECT r.rowid, r.date, r.amount, i.name, i.servingSize, i.calories, i.protein FROM records r
        JOIN items i ON r.food = i.name
        WHERE r.date = ?
        '''

        res = cursor.execute(query, (search_date,))

        return res.fetchall()


    def insert_record(self, record: Record):
        cursor = self._conn.cursor()

        cursor.execute('INSERT INTO records VALUES (?, ?, ?)',
                       (record.date, record.food, record.amt))

        self._conn.commit()


    def delete_record(self, rowid: int):
        cursor = self._conn.cursor()

        cursor.execute('DELETE FROM records WHERE rowid = ?', (rowid,))

        self._conn.commit()


    def has_items(self) -> bool:
        cursor = self._conn.cursor()

        res = cursor.execute('SELECT * FROM items LIMIT 1')

        return res.fetchone() is not None

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