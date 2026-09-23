import contextlib
import io
import unittest
from unittest.mock import patch

import app_launcher
from plugin_service import PluginServiceError


class LauncherTests(unittest.TestCase):
    def test_requires_exactly_two_devices(self):
        devices = [{"id": "one"}, {"id": "two"}]
        self.assertEqual((devices[0], devices[1]), app_launcher.choose_only_pair(devices))
        with self.assertRaisesRegex(PluginServiceError, "exactly two"):
            app_launcher.choose_only_pair(devices[:1])

    def test_rejects_invalid_host_without_connecting(self):
        with patch("app_launcher.PluginService") as service:
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(2, app_launcher.main(["3"]))
            service.assert_not_called()

    def test_switches_discovered_pair(self):
        with patch("app_launcher.PluginService") as service:
            client = service.return_value.__enter__.return_value
            client.devices.return_value = [{"id": "mouse"}, {"id": "keyboard"}]
            self.assertEqual(0, app_launcher.main(["1"]))
            client.switch_pair.assert_called_once_with("mouse", "keyboard", 1)

    def test_reports_service_failure(self):
        with patch("app_launcher.PluginService", side_effect=PluginServiceError("offline")):
            with contextlib.redirect_stderr(io.StringIO()) as error:
                self.assertEqual(1, app_launcher.main(["0"]))
            self.assertIn("offline", error.getvalue())


if __name__ == "__main__":
    unittest.main()
