import subprocess
import time
import logging

class PrintQueue:
    _queue = []

    def add(self, file_name):
        self._queue.append(file_name)

    def in_queue(self, file_name):
        return file_name in self._queue
    
    def feed_into_printer(self):
        while True:
            time.sleep(1)

            if self._queue.__len__() == 0:
                continue
            
            proc = subprocess.Popen(
                'lpstat -o',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            printer_job_count = str(proc.stdout.read()).count("\n")

            if printer_job_count <= 2:
                logging.info("FED REQUEST INTO PRINTER")
                self._queue.pop(0)
        