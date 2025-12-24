from datetime import datetime
import logging
import sqlite3
import datetime

logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)


def maybe_create_table(sqlite_file: str) -> bool:
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()

    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS logs (
            date        DATETIME DEFAULT CURRENT_TIMESTAMP, 
            job_id      TEXT NOT NULL, 
            status      TEXT CHECK (status IN ('created', 'acknowledged', 'completed')) NOT NULL DEFAULT 'created',
            PRIMARY KEY (date, job_id)
            )
        """

        cursor.execute(create_table_query)
        db.commit()
        return True
    except Exception:
        logging.exception("Unable to create printer table")
        return False


def insert_print_job(sqlite_file: str, job_id: str):
    try:
        with sqlite3.connect(sqlite_file, timeout=10.0) as conn:
            cursor = conn.cursor()

            """
            yes i know we could do 

            INSERT INTO logs (job_id, status, date) 
            VALUES (?, 'created', CURRENT_TIMESTAMP)
            ON CONFLICT(job_id) DO UPDATE SET 
                status = excluded.status,
                date = excluded.date;

            but i dont care i dont feel like updating the schema on the real server
            """
            cursor.execute("DELETE FROM logs WHERE job_id = ?", (job_id,))

            sql = "INSERT INTO logs (job_id, status, date) VALUES (?, 'created', CURRENT_TIMESTAMP)"
            cursor.execute(sql, (job_id,))

            conn.commit()
            return datetime.datetime.now()
    except sqlite3.IntegrityError:
        return None
    except Exception:
        logging.exception("Inserting print job had an error")
        return None


def mark_jobs_with_status(sqlite_file, jobs, status):
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    job_ids = [(job_id,) for job_id in jobs]
    if not job_ids:
        return
    logging.debug(f"marking {job_ids} as {status} in sqlite")

    sql_update = (
        f"UPDATE logs SET status = '{status}' WHERE job_id = ?"
    )
    cursor.executemany(sql_update, job_ids)

    db.commit()


def mark_jobs_acknowledged(sqlite_file, jobs):
    mark_jobs_with_status(sqlite_file, jobs, "acknowledged")


def mark_jobs_completed(sqlite_file, jobs):
    mark_jobs_with_status(sqlite_file, jobs, "completed")
