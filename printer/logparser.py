import sqlite3
import subprocess
import datetime

try:
        
    mydb = sqlite3.connect("printer_jobs.db")
    mycursor = mydb.cursor()
    sql = "CREATE TABLE IF NOT EXISTS entries(date VARCHAR(255), job_id VARCHAR(255), PRIMARY KEY (date, job_id))"
    mycursor.execute(sql)

    CMD = "lpstat -o HP_LaserJet_p2015dn_Right"
    p = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p.wait()

    if p.returncode != 0: 
        raise subprocess.CalledProcessError(p.returncode, CMD)
    
    output = p.stdout.read()
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
        print(x[0])
        print("job id: " + x[1])
    
except Exception as e:
    print(f"An error occurred: {e}")


