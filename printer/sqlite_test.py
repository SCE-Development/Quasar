import datetime
import tempfile
import unittest
import sqlite3
import sqlite_helpers
from unittest import mock

class TestDatabaseSetup(unittest.TestCase):
    """
    - sqlite table gets created
    - inserting a log with just the job id creates a row with all the default values
    - create a few rows, then call update_completed_jobs and verify that each row has its state column updated
    """

    EXAMPLE_DATETIME = datetime.datetime(1996, 12, 24, 12, 0, 0)
    EXAMPLE_JOB_ID = "job_id-1"


    def test_maybe_create_table(self):
        with tempfile.NamedTemporaryFile() as tmp:
            result = sqlite_helpers.maybe_create_table(tmp.name)
            self.assertTrue(result)

            db = sqlite3.connect(tmp.name)
            cursor = db.cursor()    
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='logs';"
            )
            # get first element in response, cursor.fetchone() returns ('urls',)
            [table] = cursor.fetchone()
            self.assertEqual(table, "logs")

    
    @mock.patch("sqlite_helpers.datetime")
    def test_insert_log(self, mock_datetime):
        mock_datetime.fromisoformat.return_value = self.EXAMPLE_DATETIME
        mock_datetime.now.return_value = self.EXAMPLE_DATETIME

        with tempfile.NamedTemporaryFile() as tmp:
            result = sqlite_helpers.maybe_create_table(tmp.name)
            self.assertTrue(result)
            result = sqlite_helpers.insert_print_job(tmp.name, self.EXAMPLE_JOB_ID)
            self.assertEqual(result, self.EXAMPLE_DATETIME)
            
            db = sqlite3.connect(tmp.name)
            cursor = db.cursor()
            cursor.execute("SELECT * FROM logs WHERE job_id = ?", (self.EXAMPLE_JOB_ID,))
            [date, job_id, status] = cursor.fetchone()
            
            expected_datetime_str = self.EXAMPLE_DATETIME.strftime('%Y-%m-%d %H:%M:%S')
            self.assertEqual(date, expected_datetime_str)
            self.assertEqual(job_id, self.EXAMPLE_JOB_ID)
            self.assertEqual(status, 'created')
   
    @mock.patch("sqlite_helpers.datetime")
    def test_update_completed_log(self, mock_datetime):
        mock_datetime.fromisoformat.return_value = self.EXAMPLE_DATETIME
        mock_datetime.now.return_value = self.EXAMPLE_DATETIME

        # add some job ids and stuff
        with tempfile.NamedTemporaryFile() as tmp:
            result = sqlite_helpers.maybe_create_table(tmp.name)
            self.assertTrue(result)
            other_job_id = "hi i am another cool job."
            sqlite_helpers.insert_print_job(tmp.name, self.EXAMPLE_JOB_ID)
            sqlite_helpers.insert_print_job(tmp.name, other_job_id)
            sqlite_helpers.update_completed_jobs(tmp.name, {self.EXAMPLE_JOB_ID, other_job_id}, {other_job_id})
            
            db = sqlite3.connect(tmp.name)
            cursor = db.cursor()
            cursor.execute("SELECT * FROM logs WHERE job_id = ?", (self.EXAMPLE_JOB_ID,))
            [date, job_id, status] = cursor.fetchone()
            
            expected_datetime_str = self.EXAMPLE_DATETIME.strftime('%Y-%m-%d %H:%M:%S')
            self.assertEqual(date, expected_datetime_str)
            self.assertEqual(job_id, self.EXAMPLE_JOB_ID)
            self.assertEqual(status, 'completed')

if __name__ == "__main__":
    unittest.main()
    