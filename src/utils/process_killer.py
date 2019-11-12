import psutil
from logging import getLogger

logger = getLogger('autoban')

from subprocess import check_output


def kill_process(proc_name: str):
    try:
        if proc_name is not None:
            processes = tuple(map(int, check_output(["pidof", proc_name]).split()))
            for process in processes:
                proc = psutil.Process(process)
                status = proc.status()
                if status in (psutil.STATUS_SLEEPING, psutil.STATUS_ZOMBIE):
                    proc.kill()
    except Exception as e:
        logger.warning(e)
