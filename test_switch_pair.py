import argparse
import contextlib
import io
import unittest
from unittest.mock import patch

import switch_pair


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.devices = [
            {"id": "mouse", "displayName": "Old Mouse"},
            {"id": "keys", "displayName": "New Keyboard"},
        ]

    def test_automatic_pair_requires_exactly_two(self):
        self.assertEqual(tuple(self.devices), switch_pair.choose_pair(self.devices))
        with self.assertRaisesRegex(switch_pair.PairSelectionError, "exactly two"):
            switch_pair.choose_pair(self.devices[:1])

    def test_selectors_are_both_required(self):
        with self.assertRaisesRegex(switch_pair.PairSelectionError, "supplied together"):
            switch_pair.choose_pair(self.devices, "mouse", None)

    def test_selects_by_name_or_id(self):
        selected = switch_pair.choose_pair(self.devices, "old", "keys")
        self.assertEqual((self.devices[0], self.devices[1]), selected)

    def test_dry_run_never_executes(self):
        args = argparse.Namespace(
            timeout=3.0, first=None, second=None, host=2, execute=False
        )
        with patch("switch_pair.PluginService") as service:
            client = service.return_value.__enter__.return_value
            client.devices.return_value = self.devices
            with contextlib.redirect_stdout(io.StringIO()) as output:
                switch_pair.command_switch(args)
            self.assertIn("Dry run", output.getvalue())
            client.switch_pair.assert_not_called()

    def test_cli_converts_physical_host_to_zero_based_channel(self):
        args = argparse.Namespace(
            timeout=3.0, first=None, second=None, host=3, execute=True
        )
        with patch("switch_pair.PluginService") as service:
            client = service.return_value.__enter__.return_value
            client.devices.return_value = self.devices
            client.switch_pair.return_value = 0.01
            with contextlib.redirect_stdout(io.StringIO()):
                switch_pair.command_switch(args)
            client.switch_pair.assert_called_once_with("mouse", "keys", 2)


if __name__ == "__main__":
    unittest.main()
