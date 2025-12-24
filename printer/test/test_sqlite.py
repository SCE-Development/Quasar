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
        self.assertEqual(status, "created")

    def test_insert_log_overwrites_existing(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()
        sqlite_helpers.maybe_create_table(db_path)

        date_in_2023 = '2023-12-24 23:50:00'
        
        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO logs (job_id, status, date) VALUES (?, ?, '2023-12-24 23:50:00')",
                (self.EXAMPLE_JOB_ID, "completed")
            )
            db.commit()

        new_timestamp = sqlite_helpers.insert_print_job(db_path, self.EXAMPLE_JOB_ID)
        self.assertIsNotNone(new_timestamp)

        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()
            
            cursor.execute("SELECT date, job_id, status FROM logs WHERE job_id = ?", (self.EXAMPLE_JOB_ID,))
            rows = cursor.fetchall()

            self.assertEqual(len(rows), 1, "Database should not have duplicate job_ids")

            (db_date_str, _, db_status) = rows[0]

            self.assertEqual(db_status, "created", "Status has been reset to 'created'")

            self.assertNotEqual(db_date_str, date_in_2023, "The date should have been updated to now")
            
            current_year = str(datetime.datetime.now().year)
            self.assertIn(current_year, db_date_str, f"Expected timestamp to contain {current_year}")
            
            # Cleanup
            os.unlink(db_path)

    def test_mark_jobs_acknowledged(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(result)

        sqlite_helpers.insert_print_job(tmp.name, "hello")
        sqlite_helpers.insert_print_job(tmp.name, "world")

        sqlite_helpers.mark_jobs_acknowledged(tmp.name, ["hello"])
        db = sqlite3.connect(tmp.name)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM logs WHERE job_id = ?", ("hello",))
        [_, job_id, status] = cursor.fetchone()
        self.assertEqual(job_id, "hello")
        self.assertEqual(status, "acknowledged")

        cursor.execute("SELECT * FROM logs WHERE job_id = ?", ("world",))
        [_, job_id, status] = cursor.fetchone()
        self.assertEqual(job_id, "world")
        self.assertEqual(status, "created")

    def test_mark_jobs_completed(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(result)

        sqlite_helpers.insert_print_job(tmp.name, "hello")
        sqlite_helpers.insert_print_job(tmp.name, "world")

        sqlite_helpers.mark_jobs_completed(tmp.name, ["hello", "world"])

        db = sqlite3.connect(tmp.name)
        cursor = db.cursor()
        cursor.execute("SELECT job_id FROM logs WHERE status = 'completed'")
        stuff = cursor.fetchall()
        # make sure it has length

        self.assertEqual(len(stuff), 2)
        job_ids = [row[0] for row in stuff]
        self.assertCountEqual(job_ids, ["hello", "world"])


if __name__ == "__main__":
    unittest.main()
