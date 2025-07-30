import subprocess
import sqlite_helpers
import sqlite3
import tempfile
import unittest
from unittest import mock

import gerard

class TestLpStatSqlite(unittest.TestCase):

    def setUp(self):
        gerard.jobs_seen_last.clear()
        gerard.current_jobs.clear()


    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_parsing_single(self, mock_popen):
        job_id = "print_job-1"
        mock_popen_result = mock.MagicMock()
        mock_popen_result.returncode = 0
        mock_popen_result.stdout.read.return_value = job_id
        mock_popen.return_value = mock_popen_result

        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        db_result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(db_result)

        gerard.query_lpstat(db_path, gerard.LPSTAT_CMD)
        self.assertEqual(gerard.jobs_seen_last, {job_id})

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_acknowledged_single(self, mock_popen):
        job_id  = "print_job-1"

        mock_popen_result = mock.MagicMock()
        mock_popen_result.returncode = 0
        mock_popen_result.stdout.read.return_value = job_id
        mock_popen.return_value = mock_popen_result

        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        db_result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(db_result)
        insert_result = sqlite_helpers.insert_print_job(db_path, job_id)
        self.assertIsNotNone(insert_result)

        gerard.query_lpstat(db_path, gerard.LPSTAT_CMD)

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

        self.assertEqual(gerard.jobs_seen_last, {job_id})

    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_completed_single(self, mock_popen):
        job_id  = "print_job-1"

        mock_popen_result = mock.MagicMock()
        mock_popen_result.returncode = 0
        mock_popen_result.stdout.read.return_value = ""
        mock_popen.return_value = mock_popen_result

        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        db_result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(db_result)
        insert_result = sqlite_helpers.insert_print_job(db_path, job_id)
        self.assertIsNotNone(insert_result)

        gerard.jobs_seen_last.update({job_id})
        gerard.query_lpstat(db_path, gerard.LPSTAT_CMD)
        
        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

        self.assertEqual(gerard.jobs_seen_last, set())
        
    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_parsing_multiple(self, mock_popen):
        job_id_1 = "print_job-1"
        job_id_2 = "print_job-2"
        mock_popen_result = mock.MagicMock()
        mock_popen_result.returncode = 0
        mock_popen_result.stdout.read.return_value = f"{job_id_1}\n{job_id_2}"
        mock_popen.return_value = mock_popen_result

        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        db_result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(db_result)

        gerard.query_lpstat(db_path, gerard.LPSTAT_CMD)
        self.assertEqual(gerard.jobs_seen_last, {job_id_1, job_id_2})

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

    
    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_acknowledged_multiple(self, mock_popen):
        
        job_id_1  = "print_job-1"
        job_id_2 = "print_job-2"

        mock_popen_result = mock.MagicMock()
        mock_popen_result.returncode = 0
        mock_popen_result.stdout.read.return_value = job_id_1 + '\n' + job_id_2
        mock_popen.return_value = mock_popen_result

        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        db_result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(db_result)
        insert_1 = sqlite_helpers.insert_print_job(db_path, job_id_1)
        self.assertIsNotNone(insert_1)
        insert_2 = sqlite_helpers.insert_print_job(db_path, job_id_2)
        self.assertIsNotNone(insert_2)

        gerard.query_lpstat(db_path, gerard.LPSTAT_CMD)

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )
        self.assertEqual(gerard.jobs_seen_last, {job_id_1, job_id_2})

    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_completed_multiple(self, mock_popen):
        job_id_1  = "print_job-1"
        job_id_2 = "print_job-2"

        mock_popen_result = mock.MagicMock()
        mock_popen_result.returncode = 0
        mock_popen_result.stdout.read.return_value = ""
        mock_popen.return_value = mock_popen_result

        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        db_result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(db_result)
        insert_result = sqlite_helpers.insert_print_job(db_path, job_id_1)
        self.assertIsNotNone(insert_result)
        insert_2 = sqlite_helpers.insert_print_job(db_path, job_id_2)
        self.assertIsNotNone(insert_2)

        gerard.jobs_seen_last.update({job_id_1, job_id_2})
        gerard.query_lpstat(db_path, gerard.LPSTAT_CMD)

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )


        self.assertEqual(gerard.jobs_seen_last, set())


    @mock.patch("gerard.subprocess.Popen")
    def test_query_lpstat_one_completed_from_multiple(self, mock_popen):
        job_id_1  = "print_job-1"
        job_id_2 = "print_job-2"

        mock_popen_result = mock.MagicMock()
        mock_popen_result.returncode = 0
        mock_popen_result.stdout.read.return_value = job_id_2
        mock_popen.return_value = mock_popen_result

        tmp = tempfile.NamedTemporaryFile(delete=False)
        db_path = tmp.name
        tmp.close()

        db_result = sqlite_helpers.maybe_create_table(db_path)
        self.assertTrue(db_result)
        insert_result = sqlite_helpers.insert_print_job(db_path, job_id_1)
        self.assertIsNotNone(insert_result)
        insert_2 = sqlite_helpers.insert_print_job(db_path, job_id_2)
        self.assertIsNotNone(insert_2)

        gerard.jobs_seen_last.update({job_id_1, job_id_2})
        gerard.query_lpstat(db_path, gerard.LPSTAT_CMD)

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )
        self.assertEqual(gerard.jobs_seen_last, {job_id_2})

if __name__ == "__main__":
    unittest.main()