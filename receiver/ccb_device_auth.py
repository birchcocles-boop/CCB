from http.cookies import SimpleCookie
from ccb_auth import authorized
from ccb_devices import validate

def authorized_request(request):
    if authorized(request.headers.get("X-CCB-Admin-Token")):
        return True

    raw = request.headers.get_all("Cookie", [])
    if len(raw) != 1 or len(raw[0]) > 4096:
        return False

    try:
        cookies = SimpleCookie()
        cookies.load(raw[0])
        device = cookies.get("ccb_device")
        return device is not None and validate(device.value)
    except (ValueError, TypeError):
        return False
