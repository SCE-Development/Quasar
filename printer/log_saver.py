import sqlite3
import subprocess
import datetime
import time
import logging
import random
from dataclasses import dataclass

@dataclass
class PrinterJob:
    timestamp: str
    job_id: str

logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)

DEBUG = True
QUERY_CMD = "lpstat -o HP_LaserJet_p2015dn_Right"
running_print_jobs = set()
mydb = sqlite3.connect("printer_jobs.db")
mycursor = mydb.cursor()
sql = '''
CREATE TABLE IF NOT EXISTS entries(
    date        TEXT NOT NULL, 
    job_id      TEXT NOT NULL, 
    p_status    TEXT CHECK (p_status IN ('PRINTING', 'PENDING', 'COMPLETED', 'FAILED')) NOT NULL,
    PRIMARY KEY (date, job_id)
)'''
mycursor.execute(sql)


def print_db():
    sql_query = "SELECT * FROM entries"
    mycursor.execute(sql_query)
    for x in mycursor.fetchall():
        logging.info(x)

def get_time_and_id(line):
    cleaned_output = line.strip().split(" ")
    job_id = cleaned_output[0]
    
    output_dt = cleaned_output[:-7:-1]
    output_dt_str = " ".join(output_dt[::-1]).strip()
    date_obj = datetime.datetime.strptime(output_dt_str, "%a %b %d %H:%M:%S %Y")
    date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    return PrinterJob(timestamp=date_str, job_id=job_id)

def call_lpstat_popen(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p.wait()

    if p.returncode != 0: 
        raise subprocess.CalledProcessError(p.returncode, cmd)
    
    output = p.stdout.read().strip()
    if len(output) == 0:
        return None
    
    # 2 things at once; add new jobs to new one while also retrieving current job_ids
    return output.split("\n")

def update_completed_jobs(current_jobs):
    global running_print_jobs

     # everything in the previous run that IS NOT in the current run
    completed_jobs = running_print_jobs.difference(current_jobs)    
    for job_id in completed_jobs:
        sql_update = '''
        UPDATE entries SET p_status = 'COMPLETED' WHERE job_id = ?
        '''
        mycursor.execute(sql_update, job_id)
        mydb.commit()

    logging.info(f"\nthis is the running jobs {running_print_jobs}\nand this is the current jobs {current_jobs}")
    running_print_jobs.update(running_print_jobs - completed_jobs)




def query_printer_jobs(cmd):
    #logging.info(date_str + " " + job_id)
    jobs = call_lpstat_popen(cmd)
    current_jobs = set()
    if not jobs:
        # that means we are done in some way
        # TODO: should i add code here to remove everything in sqlite database since no jobs?
        update_completed_jobs(current_jobs)
        return

    global running_print_jobs

    for job in jobs:
        print_job_dataclass = get_time_and_id(job)
        job_id = print_job_dataclass.job_id
        timestamp = print_job_dataclass.timestamp
                
        current_jobs.add(job_id)

        if job_id in running_print_jobs:
            continue

        running_print_jobs.add(job_id) 
        sql_insert = '''
        INSERT INTO entries (date, job_id, p_status) VALUES (?, ?, 'PRINTING')
        '''
        mycursor.execute(sql_insert, (timestamp, job_id))
        mydb.commit()

        update_completed_jobs(current_jobs)


    if DEBUG:
        print_db()

def test_job_ids():
    x = random.randint(1,1)
    MOCK_CMD  = f"echo HP_LaserJet_p2015dn_Right-{x} root              5120   {datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y')}"
    DONE_CMD = ""
    for n in range(x):
        query_printer_jobs(MOCK_CMD)
        time.sleep(1)
    query_printer_jobs(DONE_CMD)

def simulate_printer_jobs():
    
    test_job_ids()
    # time.sleep(0.5)
    # test_job_ids()

if __name__ == "__main__":
    # This will run the query_printer_jobs function every second
    # and print the job id and date from the database.
    if DEBUG:
        simulate_printer_jobs()
    else:
        while True:     
            try:
                query_printer_jobs(QUERY_CMD)
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error querying printer jobs: {e}")
                break


