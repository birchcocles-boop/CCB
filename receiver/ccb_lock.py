import fcntl
from pathlib import Path

LOCK = Path.home() / ".config/calyx-command-bridge/runner.lock"

def acquire():
    LOCK.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    handle = LOCK.open("a+")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError("CCB sandbox is already busy")
    return handle
