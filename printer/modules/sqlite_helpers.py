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
        with sqlite3.connect(sqlite_file, timeout=10.0) as db:
            cursor = db.cursor()
            timestamp = datetime.datetime.now()
            db = sqlite3.connect(sqlite_file)
            sql = "INSERT INTO logs (job_id) VALUES (?)"
            cursor.execute(sql, (job_id,))
            db.commit()
            return timestamp
    except sqlite3.IntegrityError:
        return None
    except Exception:
        logging.exception("Inserting print job had an error")
        return None


def mark_jobs_with_status(sqlite_file, jobs, status):
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()

    logging.info(f"marking {jobs} as {status} in sqlite")

    sql_update = (
        f"UPDATE logs SET status = {status} WHERE job_id = ? AND status != {status}"
    )
    cursor.executemany(sql_update, jobs)

    db.commit()


def mark_jobs_acknowledged(sqlite_file, jobs):
    mark_jobs_with_status(sqlite_file, jobs, "acknowledged")


def mark_jobs_completed(sqlite_file, jobs):
    mark_jobs_with_status(sqlite_file, jobs, "completed")


def update_jobs(sqlite_file, jobs_seen_last, current_jobs):

    # everything in the previous set that IS NOT in the current set
    completed_jobs = jobs_seen_last.difference(current_jobs)
    completed_job_ids = [(job_id,) for job_id in completed_jobs]
    current_job_ids = [(job_id,) for job_id in current_jobs]

    sql_update = "UPDATE logs SET status = 'completed' WHERE job_id = ?"
    cursor.executemany(sql_update, completed_job_ids)

    sql_set_acknowledged = "UPDATE logs SET status = 'acknowledged' WHERE job_id = ? AND status != 'acknowledged'"
    cursor.executemany(sql_set_acknowledged, current_job_ids)

    jobs_seen_last.clear()
    jobs_seen_last.update(current_jobs.copy())
    current_jobs.clear()
