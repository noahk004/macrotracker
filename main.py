import os
from pathlib import Path
from dotenv import load_dotenv
from engine import Engine
from db import DB


if __name__ == '__main__':

    load_dotenv()

    ENVIRONMENT = os.getenv('MACROTRACKER_ENVIRONMENT')

    db_path = 'macrotracker.db'

    db = DB(Path.cwd() / db_path)

    engine = Engine(db)

    engine.start()