import json
import os
import subprocess
from ccb_device_auth import authorized_request
from ccb_container_runner import execute

def handle(request):
    if not os.environ.get("CCB_PUBLIC_HOST"):
        return 503, {"error": "Public hostname not configured"}
    origin = request.headers.get("Origin")
    host = request.headers.get("Host", "")
    if origin != ("https://" + os.environ.get("CCB_PUBLIC_HOST", "")):
        return 403, {"error": "Origin rejected"}
    if host != os.environ.get("CCB_PUBLIC_HOST", ""):
        return 403, {"error": "Host rejected"}
    if request.headers.get("Transfer-Encoding"):
        return 400, {"error": "Unsupported transfer encoding"}
    if request.headers.get("Content-Length") is None:
        return 411, {"error": "Content-Length required"}

    if not authorized_request(request):
        return 401, {"error": "Unauthorized"}

    if request.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
        return 415, {"error": "JSON required"}

    try:
        length = int(request.headers.get("Content-Length", "0"))
    except ValueError:
        return 400, {"error": "Invalid length"}

    if length < 1 or length > 20000:
        return 413, {"error": "Request too large"}

    try:
        payload = json.loads(request.rfile.read(length))
    except (ValueError, UnicodeDecodeError):
        return 400, {"error": "Invalid JSON"}

    if not isinstance(payload, dict) or not isinstance(payload.get("script"), str):
        return 400, {"error": "Expected script string"}

    try:
        return 200, execute(payload["script"])
    except ValueError as exc:
        return 400, {"error": str(exc)}
    except RuntimeError as exc:
        if str(exc) == "CCB sandbox is already busy":
            return 409, {"error": "Sandbox busy"}
        return 503, {"error": "Sandbox unavailable"}
    except (OSError, subprocess.SubprocessError):
        return 503, {"error": "Sandbox unavailable"}
