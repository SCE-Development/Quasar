"""
## changes for rn
- sqlite_helpers.py should only contain code that has to do with inserting and querying job ids
- follow the below doc to create an iterator that will return an incrementing number
    https://docs.google.com/document/d/1OUAKLbre3m9d6-gywAfYpqgTGErKRRWy_UAHWk1D67A/edit?tab=t.0#heading=h.kce7czbd2le8
    - we will use the above to create the numerical suffix for the job id, not sqlite
- abstract the below code to a function called create_print_job. it will return a string print job id, or None if there was some error
```
print_job = subprocess.Popen(
    command,
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
print_job.wait()

if print_job.returncode != 0:
    logging.error(
        f"command returned code {print_job.returncode} stderr: {print_job.stderr.read()} stdout: {print_job.stdout.read()}"
    )
    return None
try:
    print_id = print_job.stdout.read().strip().split(" ")[3]
```
- once we have the above working, add an if statement for if we are in dev mode
- if we are in dev mode, create a fake print job and return it
- make sure ur code writes this dynamically generated job id to sqlite

**make a pr with just the above changes, the movement of job id to a function and the creation of the iterator class**
once this is done, we will discuss how to mock lpstat job ids, like how to match up the numbers with what the iterator returns

"""


import logging
import sqlite3
import time
import subprocess
import sqlite_helpers

LPSTAT_CMD = "lpstat -o HP_LaserJet_p2015dn_Right"
DEBUG_PTH = "./tmp.db"
DEBUG = False
SLEEP_TIME = 1

running_jobs = set()
current_jobs = set()
logger = logging.getLogger(__name__)

class IDIterator:
    
    def __init__(self):
        self._current = 0
    def __next__(self):
        id = self._current
        self._current += 1
        return id
    
iter = IDIterator()


def create_print_job(cmd=""):
    if DEBUG:
        job_id = f"HP_LaserJet_p2015dn_Right-{next(iter)}"
        sqlite_helpers.insert_print_job(DEBUG_PTH, job_id)
        return job_id
    
    print_job = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    print_job.wait()

    if print_job.returncode != 0:
        logging.error(
            f"command returned code {print_job.returncode} stderr: {print_job.stderr.read()} stdout: {print_job.stdout.read()}"
        )
        return None
    try:
        print_id = print_job.stdout.read().strip().split(" ")[3]
        return print_id
    except Exception as e:
        logging.error(f"There was an error printing: {e}")
        return None



def print_db(sqlite_file: str):
    sql_query = "SELECT * FROM logs"
    db = sqlite3.connect(sqlite_file)
    cursor = db.cursor()
    cursor.execute(sql_query)
    print("-------------------------------")
    for x in cursor.fetchall():
        print(x)
    print("-------------------------------")


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

