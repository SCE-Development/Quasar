from datetime import datetime
import logging
import sqlite3
import typing
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)

def maybe_create_table(sqlite_file: str) -> bool:
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()

    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS logs (
            date        DATETIME DEFAULT CURRENT_TIMESTAMP, 
            job_id      TEXT NOT NULL, 
            status      TEXT CHECK (status IN ('pending', 'completed')) NOT NULL DEFAULT 'pending',
            PRIMARY KEY (job_id)
            )
        """

        cursor.execute(create_table_query)
        db.commit()
        return True
    except Exception:
        logger.exception("Unable to create printer table")
        return False


def insert_print_job(sqlite_file: str, job_id: str):
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    timestamp = datetime.now()
    try:
        sql = "INSERT INTO logs(job_id) VALUES (?)"
        cursor.execute(sql, (job_id,))
        db.commit()
        return timestamp
    except sqlite3.IntegrityError:
        return None
    except Exception:
        logger.exception("Inserting print job had an error")
        return None

def get_urls(sqlite_file):
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    
    sql = f"""
    SELECT * FROM logs 
    ORDER BY date
    """
    cursor.execute(sql)
    result = cursor.fetchall()
    return result
