import os
from ccb_auth import authorized
from ccb_devices import issue

ORIGIN = "https://" + os.environ.get("CCB_PUBLIC_HOST", "")
HOST = os.environ.get("CCB_PUBLIC_HOST", "")

def handle(request):
    if not HOST:
        return 503, {"error": "Public hostname not configured"}, None
    if request.headers.get("Origin") != ORIGIN:
        return 403, {"error": "Origin rejected"}, None
    if request.headers.get("Host") != HOST:
        return 403, {"error": "Host rejected"}, None
    if request.headers.get("Transfer-Encoding"):
        return 400, {"error": "Unsupported encoding"}, None
    if request.headers.get("Content-Length") != "0":
        return 400, {"error": "Expected empty body"}, None
    if not authorized(request.headers.get("X-CCB-Admin-Token")):
        return 401, {"error": "Unauthorized"}, None

    device_id, token = issue("Browser device")
    cookie = (
        f"ccb_device={token}; Path=/api/; Max-Age=2592000; "
        "Secure; HttpOnly; SameSite=Strict"
    )
    return 200, {"paired": True, "device_id": device_id}, cookie
