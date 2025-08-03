import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

# this allows imports from the modules folder to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import modules
print("MUSTARD", dir(modules))
from modules import sqlite_helpers
from modules import lpstat_helpers


class TestLpStatSqlite(unittest.TestCase):

    def setUp(self):
        lpstat_helpers.jobs_seen_last.clear()
        lpstat_helpers.current_jobs.clear()


    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
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

        lpstat_helpers.query_lpstat(db_path, lpstat_helpers.LPSTAT_CMD)
        self.assertEqual(lpstat_helpers.jobs_seen_last, {job_id})

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                lpstat_helpers.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
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

        lpstat_helpers.query_lpstat(db_path, lpstat_helpers.LPSTAT_CMD)

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                lpstat_helpers.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

        self.assertEqual(lpstat_helpers.jobs_seen_last, {job_id})

    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
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

        lpstat_helpers.jobs_seen_last.update({job_id})
        lpstat_helpers.query_lpstat(db_path, lpstat_helpers.LPSTAT_CMD)
        
        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                lpstat_helpers.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

        self.assertEqual(lpstat_helpers.jobs_seen_last, set())
        
    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
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

        lpstat_helpers.query_lpstat(db_path, lpstat_helpers.LPSTAT_CMD)
        self.assertEqual(lpstat_helpers.jobs_seen_last, {job_id_1, job_id_2})

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                lpstat_helpers.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

    
    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
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

        lpstat_helpers.query_lpstat(db_path, lpstat_helpers.LPSTAT_CMD)

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                lpstat_helpers.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )
        self.assertEqual(lpstat_helpers.jobs_seen_last, {job_id_1, job_id_2})

    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
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

        lpstat_helpers.jobs_seen_last.update({job_id_1, job_id_2})
        lpstat_helpers.query_lpstat(db_path, lpstat_helpers.LPSTAT_CMD)

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                lpstat_helpers.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )


        self.assertEqual(lpstat_helpers.jobs_seen_last, set())


    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
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

        lpstat_helpers.jobs_seen_last.update({job_id_1, job_id_2})
        lpstat_helpers.query_lpstat(db_path, lpstat_helpers.LPSTAT_CMD)

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                lpstat_helpers.LPSTAT_CMD,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )
        self.assertEqual(lpstat_helpers.jobs_seen_last, {job_id_2})

if __name__ == "__main__":
    unittest.main()