import gerard
import sqlite_helpers
from unittest import mock
import unittest

class TestGerardWithMockedDB(unittest.TestCase):
    def setUp(self):
        self.original_jobs_seen_last = gerard.jobs_seen_last.copy()
        self.original_current_jobs = gerard.current_jobs.copy()
        gerard.jobs_seen_last.clear()
        gerard.current_jobs.clear()

    def tearDown(self):
        gerard.jobs_seen_last = self.original_jobs_seen_last
        gerard.current_jobs = self.original_current_jobs

    @mock.patch("sqlite_helpers.sqlite3.connect")
    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_parsing_single(self, mock_popen, mock_connect):
        job_id = "print_job-1"
        mock_popen.return_value.stdout.read.return_value = job_id
        mock_popen.return_value.returncode = 0
        fake_db_path = "/fake/path.db"

        gerard.query_lpstat(fake_db_path, gerard.LPSTAT_CMD)

        mock_popen.assert_called_once()
        mock_connect.assert_called_once_with(fake_db_path)
        mock_connect.return_value.cursor.return_value.executemany.assert_called_with(
            "UPDATE logs SET status = 'acknowledged' WHERE job_id = ? AND status != 'acknowledged'",
            [(job_id,)],
        )
        self.assertEqual(gerard.current_jobs, {job_id})

    @mock.patch("sqlite_helpers.sqlite3.connect")
    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_acknowledged_single(self, mock_popen, mock_connect):
        job_id = "print_job-1"
        mock_popen.return_value.stdout.read.return_value = job_id
        mock_popen.return_value.returncode = 0
        fake_db_path = "/fake/path.db"
        mock_cursor = mock_connect.return_value.cursor.return_value

        sqlite_helpers.insert_print_job(fake_db_path, job_id)
        gerard.query_lpstat(fake_db_path, gerard.LPSTAT_CMD)

        mock_cursor.execute.assert_called_with(
            "INSERT INTO logs (job_id) VALUES (?)", (job_id,)
        )
        mock_cursor.executemany.assert_called_with(
            "UPDATE logs SET status = 'acknowledged' WHERE job_id = ? AND status != 'acknowledged'",
            [(job_id,)],
        )
        self.assertEqual(gerard.current_jobs, {job_id})

    @mock.patch("sqlite_helpers.sqlite3.connect")
    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_completed_single(self, mock_popen, mock_connect):
        job_id = "print_job-1"
        gerard.jobs_seen_last.add(job_id)
        mock_popen.return_value.stdout.read.return_value = ""
        mock_popen.return_value.returncode = 0
        fake_db_path = "/fake/path.db"

        gerard.query_lpstat(fake_db_path, gerard.LPSTAT_CMD)

        mock_connect.return_value.cursor.return_value.executemany.assert_called_with(
            "UPDATE logs SET status = 'completed' WHERE job_id = ?", [(job_id,)]
        )
        self.assertEqual(gerard.current_jobs, {})

    @mock.patch("sqlite_helpers.sqlite3.connect")
    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_parsing_multiple(self, mock_popen, mock_connect):
        job_id_1 = "print_job-1"
        job_id_2 = "print_job-2"
        mock_popen.return_value.stdout.read.return_value = f"{job_id_1}\n{job_id_2}"
        mock_popen.return_value.returncode = 0
        fake_db_path = "/fake/path.db"

        gerard.query_lpstat(fake_db_path, gerard.LPSTAT_CMD)

        mock_popen.assert_called_once()
        mock_connect.assert_called_once_with(fake_db_path)
        mock_connect.return_value.cursor.return_value.executemany.assert_called_with(
            "UPDATE logs SET status = 'acknowledged' WHERE job_id = ? AND status != 'acknowledged'",
            mock.ANY,
        )
        call_args = mock_connect.return_value.cursor.return_value.executemany.call_args[0][1]
        self.assertCountEqual(call_args, [(job_id_1,), (job_id_2,)])
        self.assertEqual(gerard.current_jobs, {job_id_1, job_id_2})

    
    @mock.patch("sqlite_helpers.sqlite3.connect")
    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_acknowledged_multiple(self, mock_popen, mock_connect):
        job_id_1 = "print_job-1"
        job_id_2 = "print_job-2"
        mock_popen.return_value.stdout.read.return_value = f"{job_id_1}\n{job_id_2}"
        mock_popen.return_value.returncode = 0
        fake_db_path = "/fake/path.db"

        gerard.query_lpstat(fake_db_path, gerard.LPSTAT_CMD)

        mock_connect.return_value.cursor.return_value.executemany.assert_called_with(
            "UPDATE logs SET status = 'acknowledged' WHERE job_id = ? AND status != 'acknowledged'",
            mock.ANY,
        )
        call_args = mock_connect.return_value.cursor.return_value.executemany.call_args[0][1]
        self.assertCountEqual(call_args, [(job_id_1,), (job_id_2,)])
        self.assertEqual(gerard.current_jobs, {job_id_1, job_id_2})

    @mock.patch("sqlite_helpers.sqlite3.connect")
    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_completed_multiple(self, mock_popen, mock_connect):
        job_id_1 = "print_job-1"
        job_id_2 = "print_job-2"
        gerard.jobs_seen_last.update({job_id_1, job_id_2})
        mock_popen.return_value.stdout.read.return_value = ""
        mock_popen.return_value.returncode = 0
        fake_db_path = "/fake/path.db"

        gerard.query_lpstat(fake_db_path, gerard.LPSTAT_CMD)

        mock_connect.return_value.cursor.return_value.executemany.assert_called_with(
            "UPDATE logs SET status = 'completed' WHERE job_id = ?",
            mock.ANY,
        )
        call_args = mock_connect.return_value.cursor.return_value.executemany.call_args[0][1]
        self.assertCountEqual(call_args, [(job_id_1,), (job_id_2,)])
        self.assertEqual(gerard.current_jobs, {})

    @mock.patch("sqlite_helpers.sqlite3.connect")
    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_one_completed_from_multiple(self, mock_popen, mock_connect):
        job_id_1 = "print_job-1"
        job_id_2 = "print_job-2"
        gerard.jobs_seen_last.update({job_id_1, job_id_2})
        mock_popen.return_value.stdout.read.return_value = job_id_2
        mock_popen.return_value.returncode = 0
        fake_db_path = "/fake/path.db"
        mock_cursor = mock_connect.return_value.cursor.return_value

        gerard.query_lpstat(fake_db_path, gerard.LPSTAT_CMD)

        expected_calls = [
            mock.call(
                "UPDATE logs SET status = 'completed' WHERE job_id = ?", [(job_id_1,)]
            ),
            mock.call(
                "UPDATE logs SET status = 'acknowledged' WHERE job_id = ? AND status != 'acknowledged'",
                [(job_id_2,)],
            ),
        ]
        mock_cursor.executemany.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(gerard.current_jobs, {job_id_2})

if __name__ == "__main__":
    unittest.main()