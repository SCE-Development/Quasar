from datetime import datetime
import logging
import sqlite3
import time
import subprocess
import datetime

LPSTAT_CMD = "lpstat -o HP_LaserJet_p2015dn_Right"
DEBUG_CMDS = ["echo HP_LaserJet_p2015dn_Right-52 root              5120   Sat May 31 18:19:38 2025", "echo HP_LaserJet_p2015dn_Right-53 root              5120   Sat May 31 18:19:39 2025"]
DEBUG_PTH = "./tmp.db"
DEBUG = True
SLEEP_TIME = 1

running_jobs = set()
current_jobs = set()
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
            PRIMARY KEY (date, job_id)
            )
        """

        cursor.execute(create_table_query)
        db.commit()
        return True
    except Exception:
        logger.exception("Unable to create printer table")
        return False

def print_db(sqlite_file: str):
    sql_query = "SELECT * FROM logs"
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    cursor.execute(sql_query)
    print("-------------------------------")
    for x in cursor.fetchall():
        print(x)
    print("-------------------------------")


def insert_print_job(sqlite_file: str, job_id: str):
    global running_jobs
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

def update_completed_jobs(sqlite_file):
    global running_jobs, current_jobs
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()

     # everything in the previous set that IS NOT in the current set
    completed_jobs = running_jobs.difference(current_jobs)    
    completed_job_ids = [(job_id,) for job_id in completed_jobs] 

    sql_update = "UPDATE logs SET status = 'completed' WHERE job_id = ?"
    cursor.executemany(sql_update, completed_job_ids)
    db.commit()
    
    running_jobs.clear()
    running_jobs.update(current_jobs)
    current_jobs.clear()

def query_lpstat(sqlite_file, cmd):
    global running_jobs, current_jobs
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p.wait()

    if p.returncode != 0: 
        print(p.stderr.read())
        raise subprocess.CalledProcessError(p.returncode, cmd)
    
    output = p.stdout.read().strip()
    if len(output) == 0:
        update_completed_jobs(sqlite_file)
        return
    # 2 things at once; add new jobs to new one while also retrieving current job_ids
    jobs =  output.split("\n")
    for job in jobs:
        job_id = job.strip().split(" ")[0]
        current_jobs.add(job_id)
        running_jobs.add(job_id) 
    
    update_completed_jobs(sqlite_file)

def poll_lpstat(sqlite_file):
    while True:
        try:
            query_lpstat(sqlite_file, LPSTAT_CMD)
        except Exception as e:
            logging.error(f"Error occured: {e}")
        time.sleep(SLEEP_TIME)


def debug_poll_lpstat():
    insert_print_job(DEBUG_PTH, "HP_LaserJet_p2015dn_Right-52")
    inserted = False
    for x in range(7):
        cmd = DEBUG_CMDS[0]
        if x > 4: 
            cmd = DEBUG_CMDS[1]
        elif x > 2:
            cmd = " & ".join(DEBUG_CMDS)
            if not inserted:
                insert_print_job(DEBUG_PTH, "HP_LaserJet_p2015dn_Right-53")
                inserted = True

        try:
            query_lpstat(DEBUG_PTH, cmd)
            print_db(DEBUG_PTH)
        except Exception as e:
            logging.error(f"Error occured: {e}")
        time.sleep(SLEEP_TIME)
   
    query_lpstat(DEBUG_PTH, "")
    print_db(DEBUG_PTH)

if DEBUG:
    maybe_create_table(DEBUG_PTH)
    debug_poll_lpstat()
