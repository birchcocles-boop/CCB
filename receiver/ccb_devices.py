import hashlib
import hmac
import json
import secrets
import time
from pathlib import Path
from threading import RLock

STORE = Path.home() / ".config/calyx-command-bridge/devices.json"
LIFETIME = 30 * 86400
LOCK = RLock()

def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()

def load():
    if not STORE.exists():
        return {}
    return json.loads(STORE.read_text())

def save(data):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.parent.chmod(0o700)
    import os
    import tempfile
    fd, name = tempfile.mkstemp(dir=STORE.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(name, 0o600)
        os.replace(name, STORE)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def issue(label="Mobile device"):
    token = secrets.token_urlsafe(48)
    device_id = secrets.token_hex(8)
    with LOCK:
        data = load()
        data[device_id] = {
            "label": str(label)[:64],
            "digest": digest(token),
            "expires": int(time.time()) + LIFETIME
        }
        save(data)
    return device_id, token

def validate(token):
    if not isinstance(token, str) or not token:
        return False
    value = digest(token)
    with LOCK:
        try:
            records = load().values()
        except (OSError, ValueError, TypeError):
            return False
        for record in records:
            if not isinstance(record, dict):
                continue
            expires = record.get("expires")
            stored = record.get("digest")
            if (type(expires) is int and expires > time.time()
                    and isinstance(stored, str)
                    and hmac.compare_digest(stored, value)):
                return True
    return False

def revoke(device_id):
    with LOCK:
        data = load()
        if device_id not in data:
            return False
        del data[device_id]
        save(data)
        return True

def list_devices():
    with LOCK:
        return {
            key: {"label": v["label"], "expires": v["expires"]}
            for key, v in load().items()
        }
