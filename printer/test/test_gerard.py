import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

# this allows imports from the modules folder to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import modules
from modules import gerard
print("MUSTARD", dir(gerard))

# def test_create_print_job():
class TestGerard(unittest.TestCase):
    # runs normally and returns parsed lpstat command
    @mock.patch("modules.gerard.subprocess.Popen")    
    def test_create_print_job(self, mock_popen):
        
        mock_popen_result = mock.MagicMock()
        mock_popen_result.stdout.read.return_value = (
            "request id is HP_LaserJet_p2015dn_Right-53 (1 file(s))"
        )
        mock_popen_result.returncode = 0
        mock_popen.return_value = mock_popen_result

        self.assertEqual(
            gerard.create_print_job(num_copies=1, maybe_page_range="1", sides="one-side", printer_name="HP_P2015_DN", file_path="/tmp/test-id"), 
            "HP_LaserJet_p2015dn_Right-53"
        )

        mock_popen.assert_called_once()

        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LP_COMMAND.format(
                    num_copies=1,
                    maybe_page_range="1",
                    sides="one-side",
                    printer_name="HP_P2015_DN",
                    file_path="/tmp/test-id"
                ),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ),
        )

    @mock.patch("modules.gerard.subprocess.Popen")    
    def test_create_print_job_nonzero_returncode(self, mock_popen):
        mock_popen_result = mock.MagicMock()
        mock_popen_result.stdout.read.return_value = (
            "mocked stdout value"
        )
        mock_popen_result.stderr.read.return_value = (
            "hello future"
        )
        mock_popen_result.returncode = 1
        mock_popen.return_value = mock_popen_result


        self.assertIsNone(gerard.create_print_job(num_copies=1,
                    maybe_page_range="",
                    sides="dark-side",
                    printer_name="HP_P2015_DN",
                    file_path="/tmp/test-id"))

        mock_popen.assert_called_once()
        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LP_COMMAND.format(
                    num_copies=1,
                    maybe_page_range="",
                    sides="dark-side",
                    printer_name="HP_P2015_DN",
                    file_path="/tmp/test-id"
                ),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ),
        )


    
    @mock.patch("modules.gerard.subprocess.Popen")    
    def test_create_print_job_cant_parse_stdout(self, mock_popen):
        mock_popen_result = mock.MagicMock()
        mock_popen_result.stdout.read.return_value = (
            "mocked stdout value"
        )
        mock_popen_result.stderr.read.return_value = (
            "hello future"
        )
        mock_popen_result.returncode = 0
        mock_popen.return_value = mock_popen_result

        self.assertEqual(gerard.create_print_job(
                    num_copies=1,
                    maybe_page_range="1",
                    sides="one-side",
                    printer_name="HP_P2015_DN",
                    file_path="/tmp/test-id"), "")
        
        mock_popen.assert_called_once()

        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                gerard.LP_COMMAND.format(
                    num_copies=1,
                    maybe_page_range="1",
                    sides="one-side",
                    printer_name="HP_P2015_DN",
                    file_path="/tmp/test-id"
                ),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ),
        )



    def test_create_print_job_cant_parse_development_mode(self):

        self.assertEqual(gerard.create_print_job(1, "1", "one-side","HP_P2015_DN", "/tmp/test-id", True),  "HP_LaserJet_p2015dn_Right-0")
        self.assertEqual(gerard.create_print_job(1, "1", "one-side","HP_P2015_DN", "/tmp/test-id", True),  "HP_LaserJet_p2015dn_Right-1")
        self.assertEqual(gerard.create_print_job(1, "1", "one-side","HP_P2015_DN", "/tmp/test-id", True),  "HP_LaserJet_p2015dn_Right-2")
        
if __name__ == "__main__":
    unittest.main()