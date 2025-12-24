import logging
import subprocess
import time

from modules import sqlite_helpers

LPSTAT_CMD = "lpstat -o -W completed HP_LaserJet_p2015dn_Right"
SLEEP_TIME = 2

jobs_seen_last = set()

logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)


def query_lpstat():
    global jobs_seen_last
    global current_jobs
    p = subprocess.Popen(
        LPSTAT_CMD,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    p.wait()

    if p.returncode != 0:
        logging.error(
            f"{LPSTAT_CMD} returned nonzero code {p.returncode} with stderr {p.stderr.read()}"
        )
        return

    output = p.stdout.read().strip()
    logging.debug(f"{LPSTAT_CMD} stdout: {output}")
    if len(output) == 0:
        return
    # 2 things at once; add new jobs to new one while also retrieving current job_ids
    jobs = output.split("\n")
    for job in jobs:
        # an example line of stdout looks like
        # HP_LaserJet_p2015dn_Right-52 root              5120   Sat May 31 18:19:38 2025
        try:
            yield job.strip().split(" ")[0]
        except:
            logging.exception(f"unable to parse job id from line {job}")
            return


def poll_lpstat(sqlite_file):
    global jobs_seen_last
    while True:
        try:
            current_jobs = set(query_lpstat())
            completed_jobs = jobs_seen_last - current_jobs

            sqlite_helpers.mark_jobs_completed(
                sqlite_file, [job for job in completed_jobs]
            )
            sqlite_helpers.mark_jobs_acknowledged(
                sqlite_file, [job for job in current_jobs]
            )

            jobs_seen_last.clear()
            jobs_seen_last.update(current_jobs)

        except Exception:
            logging.exception("what happened to query_lpstat?")
        time.sleep(SLEEP_TIME)
