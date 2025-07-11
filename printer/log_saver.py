import sqlite3
import subprocess
import datetime
import time
import logging

LINE_CMD = "echo '-----------'"
QUERY_CMD = "lpstat -o HP_LaserJet_p2015dn_Right"

logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)

mydb = sqlite3.connect("printer_jobs.db")
mycursor = mydb.cursor()
sql = "CREATE TABLE IF NOT EXISTS entries(date VARCHAR(255), job_id VARCHAR(255), PRIMARY KEY (date, job_id))"
mycursor.execute(sql)

def query_printer_jobs():
    p = subprocess.Popen(QUERY_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p.wait()

    if p.returncode != 0: 
        raise subprocess.CalledProcessError(p.returncode, QUERY_CMD)
    
    output = p.stdout.read()
    if len(output) == 0:
        logging.info("No printer jobs found.")
        return

    cleaned_output = output.strip().split(" ")
    job_id = cleaned_output[0]
    
    output_dt = cleaned_output[:-7:-1]
    output_dt_str = " ".join(output_dt[::-1])
    date_obj = datetime.datetime.strptime(output_dt_str, "%a %b  %d %H:%M:%S %Y")
    date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")

    sql_insert = "INSERT INTO entries (date, job_id) VALUES (?, ?)"
    mycursor.execute(sql_insert, (date_str, job_id))
    mydb.commit()
    
    # debug, make sure the data is inserted + the date is good.
    sql_query = "SELECT * FROM entries"
    mycursor.execute(sql_query)
    for x in mycursor.fetchall():
        logging.info(f"Date: {x[0]}, Job ID: {x[1]}")

if __name__ == "__main__":
    # This will run the query_printer_jobs function every second
    # and print the job id and date from the database.
    while True:     
        subprocess.run(LINE_CMD, shell=True)
        try:
            query_printer_jobs()
        except Exception as e:
            logging.error(f"Error querying printer jobs: {e}")
            break

        time.sleep(1)


