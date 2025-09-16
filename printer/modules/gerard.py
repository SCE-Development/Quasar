"""this file is for parsing lp command output.
epicgdog made these files so instead of calling it lp_helpers.py its gerard.py
"""

import logging
import shlex
import subprocess
from datetime import datetime

LP_COMMAND = """
lp \
    -H {hold_time} \
    -n {num_copies} {maybe_page_range} \
    -o sides={sides} \
    -o media=na_letter_8.5x11in \
    -d {printer_name} \
    {file_path}
"""

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
    is_dev_printer=False,
):
    hold_time = "immediate"
    if is_dev_printer:
        future_datetime = datetime.fromtimestamp(datetime.utcnow().timestamp() + 60)
        # per CUPS docs, -H only accepts HH:MM
        # so, rather unfortunately, a virtual print
        # will take, at minimum, 1 minute 
        hold_time = f"{future_datetime.hour}:{future_datetime.minute}"


    command = LP_COMMAND.format(
        hold_time=hold_time,
        num_copies=num_copies,
        maybe_page_range=maybe_page_range,
        sides=sides,
        printer_name=printer_name,
        file_path=file_path,
    )

    if is_development_mode and not is_dev_printer:
        logging.warning(
            f"server is in development mode, command would've been `{command}`"
        )
        job_id = f"HP_LaserJet_p2015dn_Right-{next(print_job_suffix)}" 
        return job_id

    args_list = shlex.split(command.strip())
    logging.info(f"running command {command}")
    print_job = subprocess.Popen(
        args_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    print_job.wait(timeout=3)
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
