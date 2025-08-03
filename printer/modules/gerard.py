"""this file is for parsing lp command output.
epicgdog made these files so instead of calling it lp_helpers.py its gerard.py
"""

import logging
import sqlite3
import subprocess
import time

# from modules import sqlite_helpers

LPSTAT_CMD = "lpstat -o HP_LaserJet_p2015dn_Right"
LP_COMMAND = """
lp \
    -n {num_copies} {maybe_page_range} \
    -o sides={sides} \
    -o media=na_letter_8.5x11in \
    -d {printer_name} \
    {file_path}
"""
DEBUG_PTH = "./tmp.db"
DEBUG = False
SLEEP_TIME = 1

jobs_seen_last = set()
current_jobs = set()

logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)


class IDIterator:
    def __init__(self):
        self._current = 0

    def __next__(self):
        id = self._current
        self._current += 1
        return id


print_job_suffix = IDIterator()


def create_print_job(
    num_copies,
    maybe_page_range,
    sides,
    printer_name,
    file_path,
    is_development_mode=False,
):
    command = LP_COMMAND.format(
        num_copies=num_copies,
        maybe_page_range=maybe_page_range,
        sides=sides,
        printer_name=printer_name,
        file_path=file_path,
    )

    if is_development_mode:
        logging.warning(
            f"server is in development mode, command would've been `{command}`"
        )
        job_id = f"HP_LaserJet_p2015dn_Right-{next(print_job_suffix)}"
        return job_id

    logging.info(f"running command {command}")
    print_job = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if print_job.returncode != 0:
        logging.error(
            f"print job returned nonzero code {print_job.returncode} stderr: {print_job.stderr.read()} stdout: {print_job.stdout.read()}"
        )
        return None
    try:
        lp_command_output = print_job.stdout.read()
        logging.info(f"lp command stdout was {lp_command_output}")
        print_id = lp_command_output.split(" ")[3]
        return print_id
    except Exception:
        logging.exception(f"unable to parse print job from stdout")
        return ""


def query_lpstat(sqlite_file, cmd):
    global jobs_seen_last, current_jobs
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    p.wait()

    if p.returncode != 0:
        print(p.stderr.read())
        raise subprocess.CalledProcessError(p.returncode, cmd)

    output = p.stdout.read().strip()
    if len(output) == 0:
        # sqlite_helpers.update_jobs(sqlite_file, jobs_seen_last, current_jobs)
        return
    # 2 things at once; add new jobs to new one while also retrieving current job_ids
    jobs = output.split("\n")
    for job in jobs:
        job_id = job.strip().split(" ")[0]
        current_jobs.add(job_id)
        jobs_seen_last.add(job_id)

    # sqlite_helpers.update_jobs(sqlite_file, jobs_seen_last, current_jobs)


def poll_lpstat(sqlite_file):
    while True:
        try:
            query_lpstat(sqlite_file, LPSTAT_CMD)
        except Exception:
            logging.exception("what happened to query_lpstat?")
        time.sleep(SLEEP_TIME)
