import hmac
from pathlib import Path

TOKEN_FILE = Path.home() / ".config/calyx-command-bridge/admin-token"

def authorized(candidate):
    if not isinstance(candidate, str):
        return False
    try:
        expected = TOKEN_FILE.read_text().strip()
    except OSError:
        return False
    return bool(expected) and hmac.compare_digest(candidate, expected)
