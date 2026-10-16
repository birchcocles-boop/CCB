import subprocess

def verify_clean():
    result = subprocess.run(
        ["/usr/bin/podman", "ps", "-a",
         "--filter", "name=ccb-",
         "--format", "{{.Names}}"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode:
        raise RuntimeError("Cannot verify Podman state")
    if result.stdout.strip():
        raise RuntimeError("Leftover CCB container detected")
