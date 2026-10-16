#!/usr/bin/env python3
"""Calyx v0.4 isolated Podman command runner."""

import os
import signal
from ccb_input import Writer
from ccb_lock import acquire
from ccb_guard import verify_clean
import subprocess
import sys
from ccb_output import Collector
import time
import uuid

MAX_SCRIPT = 16384
MAX_OUTPUT = 16000
TIMEOUT = 30

IMAGE = os.environ.get(
    "CCB_SANDBOX_IMAGE",
    "docker.io/library/debian@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587"
)

def execute(script):
    if not isinstance(script, str) or not script.strip():
        raise ValueError("Empty command block")

    data = script.encode("utf-8")
    if len(data) > MAX_SCRIPT:
        raise ValueError("Command block exceeds 16 KiB")

    lock = acquire()
    try:
        verify_clean()
        try:
            return _execute_locked(data)
        finally:
            verify_clean()
    finally:
        lock.close()


def _execute_locked(data):
    name = "ccb-" + uuid.uuid4().hex

    command = [
        "/usr/bin/podman", "run",
        "--rm",
        "--name", name,
        "--timeout", "15",
        "--stop-timeout", "1",
        "--interactive",
        "--network", "none",
        "--read-only",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--memory", "256m",
        "--memory-swap", "256m",
        "--cpus", "0.5",
        "--pids-limit", "32",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
        "--user", "65534:65534",
        "--env", "HOME=/tmp",
        IMAGE,
        "/bin/bash", "--noprofile", "--norc",
        "-e", "-o", "pipefail", "-s"
    ]

    start = time.monotonic()

    if True:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        collector = Collector(process.stdout, MAX_OUTPUT)
        collector.start()

        try:
            writer = Writer(process.stdin, data)
            writer.start()
            process.wait(timeout=TIMEOUT)
            exit_code = process.returncode



        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise RuntimeError("Podman watchdog expired")

        writer_error = writer.finish()
        output, was_truncated = collector.finish()
        if writer_error:
            raise RuntimeError(f'Input delivery failed: {writer_error}')

    return {
        "exit_code": exit_code,
        "stdout": output[:MAX_OUTPUT].decode(
            "utf-8", errors="replace"
        ),
        "truncated": was_truncated,
        "duration_ms": round(
            (time.monotonic() - start) * 1000
        )
    }
if __name__ == "__main__":
    script = sys.stdin.read(MAX_SCRIPT + 1)
    print(execute(script))
