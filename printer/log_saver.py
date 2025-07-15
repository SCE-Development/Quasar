import sqlite3
import subprocess
import datetime
import time
import logging
import random
import asyncio

DEBUG = True

LINE_CMD  = "echo -----------"
QUERY_CMD = "lpstat -o HP_LaserJet_p2015dn_Right"

logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)

mydb = sqlite3.connect("printer_jobs.db")
mycursor = mydb.cursor()
sql = '''
CREATE TABLE IF NOT EXISTS entries(
    date        TEXT NOT NULL DEFAULT "0000-00-00 00:00:00", 
    job_id      TEXT NOT NULL DEFAULT "0000-0000", 
    p_status    TEXT CHECK (p_status IN ('PRINTING', 'PENDING', 'COMPLETED', 'FAILED')) NOT NULL DEFAULT "PRINTING",
    PRIMARY KEY (date, job_id)
)'''
mycursor.execute(sql)

def print_db():
    sql_query = "SELECT * FROM entries"
    mycursor.execute(sql_query)
    for x in mycursor.fetchall():
        logging.info(x)

def test_job_ids():
    x = random.randint(3, 7)
    MOCK_CMD  = f"echo HP_LaserJet_p2015dn_Right-{x} root              5120   Mon Jul 7 03:43:42 2025"
    DONE_CMD = ""
    for n in range(x):
        query_printer_jobs(MOCK_CMD)
        time.sleep(1)
    query_printer_jobs(DONE_CMD)

def simulate_printer_jobs():
    
    test_job_ids()
    time.sleep(0.5)


    test_job_ids()
def query_printer_jobs(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p.wait()

    if p.returncode != 0: 
        raise subprocess.CalledProcessError(p.returncode, cmd)
    
    output = p.stdout.read()
    if len(output) == 0:
        # set everything to completed
        sql_update_completed = '''
        UPDATE entries SET p_status = 'COMPLETED' WHERE p_status = 'PRINTING'
        '''
        mycursor.execute(sql_update_completed)
        mydb.commit()
        logging.info("No jobs found, updated all to COMPLETED")

        if DEBUG:
            print_db()
        return

    
    #logging.info(output)
    cleaned_output = output.strip().split(" ")
    job_id = cleaned_output[0]
    
    output_dt = cleaned_output[:-7:-1]
    output_dt_str = " ".join(output_dt[::-1]).strip()
    date_obj = datetime.datetime.strptime(output_dt_str, "%a %b %d %H:%M:%S %Y")
    date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    #logging.info(date_str + " " + job_id)

    sql_insert = '''
    INSERT INTO entries (date, job_id) VALUES (?, ?)
    ON CONFLICT(date, job_id) DO UPDATE SET p_status = 'PRINTING'
    '''
    mycursor.execute(sql_insert, (date_str, job_id))
    mydb.commit()
    
    # debug, make sure the data is inserted + the date is good.
    if DEBUG:
        print_db()

if __name__ == "__main__":
    # This will run the query_printer_jobs function every second
    # and print the job id and date from the database.
    if DEBUG:
        simulate_printer_jobs()
    else:
        while True:     
            subprocess.run(LINE_CMD, shell=True)
            try:
                query_printer_jobs(QUERY_CMD)
            except Exception as e:
                logging.error(f"Error querying printer jobs: {e}")
                break

            time.sleep(1)


