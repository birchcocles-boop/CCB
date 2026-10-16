import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from receiver import ccb_devices


class DeviceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

        self.store = Path(self.tmp.name) / "devices.json"
        patcher = patch.object(ccb_devices, "STORE", self.store)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_issue_and_validate(self):
        device_id, token = ccb_devices.issue("Test browser")
        self.assertTrue(device_id)
        self.assertTrue(ccb_devices.validate(token))
        self.assertFalse(ccb_devices.validate("incorrect-token"))

    def test_private_permissions(self):
        ccb_devices.issue("Test browser")
        self.assertEqual(self.store.stat().st_mode & 0o777, 0o600)

    def test_revoke(self):
        device_id, token = ccb_devices.issue()
        self.assertTrue(ccb_devices.revoke(device_id))
        self.assertFalse(ccb_devices.validate(token))

    def test_corrupted_database(self):
        self.store.write_text("{invalid")
        self.assertFalse(ccb_devices.validate("test-token"))

    def test_expired_token(self):
        device_id, token = ccb_devices.issue()
        data = ccb_devices.load()
        data[device_id]["expires"] = 0
        ccb_devices.save(data)
        self.assertFalse(ccb_devices.validate(token))


if __name__ == "__main__":
    unittest.main()
