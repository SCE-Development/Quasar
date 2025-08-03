import datetime
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

# this allows imports from the modules folder to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules import sqlite_helpers


class TestDatabaseSetup(unittest.TestCase):
    """
    - sqlite table gets created
    - inserting a log with just the job id creates a row with all the default values
    - create a few rows, then call update_completed_jobs and verify that each row has its state column updated
    """

    EXAMPLE_DATETIME = datetime.datetime(1996, 12, 24, 12, 0, 0)
    EXAMPLE_JOB_ID = "job_id-1"


    def test_maybe_create_table(self):

        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()
        
        result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(result)

        db = sqlite3.connect(tmp.name)
        cursor = db.cursor()    
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='logs';"
        )
        # get first element in response, cursor.fetchone() returns ('urls',)
        [table] = cursor.fetchone()
        self.assertEqual(table, "logs")

    
    def test_insert_log(self):

        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(result)
        result = sqlite_helpers.insert_print_job(tmp.name, self.EXAMPLE_JOB_ID)
        
        db = sqlite3.connect(tmp.name)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM logs WHERE job_id = ?", (self.EXAMPLE_JOB_ID,))
        [_, job_id, status] = cursor.fetchone()
        self.assertEqual(job_id, self.EXAMPLE_JOB_ID)
        self.assertEqual(status, 'created')
   
    def test_update_completed_log(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()
        
        result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(result)

        jobs_seen_last = {self.EXAMPLE_JOB_ID, "hello", "world"}

        sqlite_helpers.insert_print_job(tmp.name, self.EXAMPLE_JOB_ID)
        sqlite_helpers.insert_print_job(tmp.name, "hello")
        sqlite_helpers.insert_print_job(tmp.name, "world")

        sqlite_helpers.update_jobs(tmp.name, jobs_seen_last, {"hello", "world"})
        
        db = sqlite3.connect(tmp.name)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM logs WHERE job_id = ?", (self.EXAMPLE_JOB_ID,))
        [_, job_id, status] = cursor.fetchone()
        self.assertEqual(job_id, self.EXAMPLE_JOB_ID)
        self.assertEqual(status, 'completed')
        
        sqlite_helpers.update_jobs(tmp.name, jobs_seen_last, {"world"})
        
        db = sqlite3.connect(tmp.name)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM logs WHERE job_id = ?", ("world",))
        [_, job_id, status] = cursor.fetchone()
        self.assertEqual(job_id, "world")
        self.assertEqual(status, 'acknowledged')

if __name__ == "__main__":
    unittest.main()
    