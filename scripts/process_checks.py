"""Bound validation processes and their descendants without invoking a shell."""
import os
import signal
import subprocess


def stop_process_tree(process):
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass
        # Also reap descendants that survived the parent or ignored SIGTERM.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def run_with_deadline(arguments, timeout):
    process = subprocess.Popen(arguments, start_new_session=os.name != 'nt',
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
    try:
        return process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        stop_process_tree(process)
        print('Validation process exceeded its deadline', flush=True)
        return 124
    except BaseException:
        stop_process_tree(process)
        raise
