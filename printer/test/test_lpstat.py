import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

# this allows imports from the modules folder to work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import modules
from modules import sqlite_helpers
from modules import lpstat_helpers


class TestLpStatSqlite(unittest.TestCase):
    LPSTAT_LINE_1 = (
        "HP_LaserJet_p2015dn_Right-52 root              5120   Sat May 31 18:19:38 2025"
    )
    LPSTAT_LINE_2 = (
        "HP_LaserJet_p2015dn_Right-53 root              5120   Sat May 31 18:19:38 2025"
    )

    # returns a single line result
    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
    def test_query_lpstat(self, mock_popen):
        mock_popen_result = mock.MagicMock()
        mock_popen_result.stdout.read.return_value = self.LPSTAT_LINE_1
        mock_popen_result.returncode = 0
        mock_popen.return_value = mock_popen_result

        self.assertEqual(
            list(lpstat_helpers.query_lpstat()), ["HP_LaserJet_p2015dn_Right-52"]
        )

    # returns multi line result
    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
    def test_query_lpstat_multiline(self, mock_popen):
        mock_popen_result = mock.MagicMock()
        mock_popen_result.stdout.read.return_value = "\n".join(
            [self.LPSTAT_LINE_1, self.LPSTAT_LINE_2]
        )
        mock_popen_result.returncode = 0
        mock_popen.return_value = mock_popen_result
        self.assertEqual(
            list(lpstat_helpers.query_lpstat()),
            ["HP_LaserJet_p2015dn_Right-52", "HP_LaserJet_p2015dn_Right-53"],
        )

    # handles bad stdout
    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
    def test_query_lpstat_bad_parse(self, mock_popen):
        mock_popen_result = mock.MagicMock()
        mock_popen_result.stdout.read.return_value = ""
        mock_popen_result.returncode = 0
        mock_popen.return_value = mock_popen_result

        self.assertEqual(list(lpstat_helpers.query_lpstat()), [])

    @mock.patch("modules.lpstat_helpers.subprocess.Popen")
    def test_query_lpstat_nonzero(self, mock_popen):
        mock_popen_result = mock.MagicMock()
        mock_popen_result.stdout.read.return_value = (
            "request id is HP_LaserJet_p2015dn_Right-53 (1 file(s))"
        )
        mock_popen_result.returncode = 1
        mock_popen.return_value = mock_popen_result

        self.assertEqual(list(lpstat_helpers.query_lpstat()), [])

    @mock.patch("modules.lpstat_helpers.sqlite_helpers.mark_jobs_completed")
    @mock.patch("modules.lpstat_helpers.sqlite_helpers.mark_jobs_acknowledged")
    @mock.patch("modules.lpstat_helpers.query_lpstat")
    @mock.patch("modules.lpstat_helpers.time.sleep", side_effect=Exception("stop loop"))
    def test_poll_lpstat(
        self, mock_sleep, mock_query_lpstat, mock_mark_acknowledged, mock_mark_completed
    ):
        # Simulate current jobs reported by lpstat
        mock_query_lpstat.return_value = [
            "HP_LaserJet_p2015dn_Right-53",
            "HP_LaserJet_p2015dn_Right-54",
        ]

        # Run poll_lpstat in try-except to break loop via sleep
        with self.assertRaises(Exception) as cm:
            lpstat_helpers.poll_lpstat("dummy.db")

        self.assertEqual(str(cm.exception), "stop loop")

        # Check correct jobs marked as completed and acknowledged
        mock_mark_completed.assert_called_once_with(
            "dummy.db", ["HP_LaserJet_p2015dn_Right-54", "HP_LaserJet_p2015dn_Right-53"],
        )


if __name__ == "__main__":
    unittest.main()
