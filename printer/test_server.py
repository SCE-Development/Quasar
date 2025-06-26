import importlib
import io
import os
import subprocess
import unittest
from unittest import mock


from fastapi.testclient import TestClient

import server


class TestFastAPI(unittest.TestCase):
    def load_server_with_args(self, argv=[]):
        argv_to_use = ["server.py"]
        argv_to_use.extend(argv)

        os.environ["RIGHT_PRINTER_NAME"] = "HP_P2015_DN"

        with mock.patch("sys.argv", argv_to_use):
            importlib.reload(server)

        return TestClient(server.app)

    def test_health_check(self):
        client = self.load_server_with_args()
        response = client.get("/healthcheck/printer")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '"printer is up!"')

    @mock.patch("server.uuid.uuid4", return_value="test-id")
    @mock.patch("server.subprocess.Popen")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("pathlib.Path.unlink")
    def test_print_endpoint(self, mock_pathlib_unlink, mock_open_func, mock_popen, _):
        client = self.load_server_with_args()
        test_file = io.BytesIO(b"dummy file content")
        response = client.post(
            "/print",
            files={"file": ("test.txt", test_file, "text/plain")},
            data={"copies": "1", "sides": "one-sided"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '"worked!"')

        mock_open_func.assert_called_once_with("/tmp/test-id", "wb")

        mock_open_func().write.assert_called_once()
        self.assertEqual(
            mock_open_func().write.call_args_list[0], mock.call(b"dummy file content")
        )

        mock_popen.assert_called_once()

        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                "lp -n 1  -o sides=one-sided -o media=na_letter_8.5x11in -d HP_P2015_DN /tmp/test-id",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ),
        )

        mock_pathlib_unlink.assert_called_once()

    @mock.patch("server.uuid.uuid4", return_value="test-id")
    @mock.patch("server.subprocess.Popen")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @mock.patch("pathlib.Path.unlink")
    def test_print_endpoint_dont_delete_pdf(
        self, mock_pathlib_unlink, mock_open_func, mock_popen, _
    ):
        client = self.load_server_with_args(["--dont-delete-pdfs"])
        test_file = io.BytesIO(b"dummy file content")
        response = client.post(
            "/print",
            files={"file": ("test.txt", test_file, "text/plain")},
            data={"copies": "1", "sides": "one-sided"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '"worked!"')

        mock_open_func.assert_called_once_with("/tmp/test-id", "wb")

        mock_open_func().write.assert_called_once()
        self.assertEqual(
            mock_open_func().write.call_args_list[0], mock.call(b"dummy file content")
        )

        mock_popen.assert_called_once()

        self.assertEqual(
            mock_popen.call_args_list[0],
            mock.call(
                "lp -n 1  -o sides=one-sided -o media=na_letter_8.5x11in -d HP_P2015_DN /tmp/test-id",
                shell=True,
            ),
        )

        mock_pathlib_unlink.assert_not_called()

    @mock.patch("server.subprocess.Popen")
    @mock.patch("builtins.open", side_effect=FileNotFoundError("sorry!"))
    @mock.patch("pathlib.Path.unlink")
    def test_print_endpoint_error(self, mock_pathlib_unlink, _, mock_popen):
        client = self.load_server_with_args()
        test_file = io.BytesIO(b"dummy file content")
        response = client.post(
            "/print",
            files={"file": ("test.txt", test_file, "text/plain")},
            data={"copies": "1", "sides": "one-sided"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status_code": 500,
                "detail": "printing failed, check logs",
                "headers": None,
            },
        )

        mock_popen.assert_not_called()
        mock_pathlib_unlink.assert_not_called()


if __name__ == "__main__":
    unittest.main()
