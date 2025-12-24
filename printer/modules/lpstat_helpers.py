import logging
import subprocess
import time

from modules import sqlite_helpers


LPSTAT_CMD = "lpstat -o -W completed HP_LaserJet_p2015dn_Right"
POLL_LPSTAT_INTERVAL_SECONDS = 2

logging.basicConfig(
    # in mondo we trust
    format="%(asctime)s.%(msecs)03dZ %(levelname)s:%(name)s:%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)


def query_lpstat():
    global current_jobs
    """
    the output of this command looks like
    ben@ben:/app# lpstat -W completed -o HP_LaserJet_p2015dn_Right
    HP_LaserJet_p2015dn_Right-3 ben              5120   Mon Dec 22 21:43:54 2025
    HP_LaserJet_p2015dn_Right-2 ben              8192   Mon Dec 22 21:43:23 2025
    HP_LaserJet_p2015dn_Right-1 ben              8192   Mon Dec 22 21:41:08 2025
    """
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
    while True:
        try:
            completed_jobs = set(query_lpstat())
            sqlite_helpers.mark_jobs_completed(
                sqlite_file, [job for job in completed_jobs]
            )

        except Exception:
            logging.exception("what happened to query_lpstat?")
        time.sleep(POLL_LPSTAT_INTERVAL_SECONDS)
