#!/usr/bin/env python3
"""Entry point bundled inside the three macOS host-switch applications."""
from __future__ import annotations

import sys

from plugin_service import PluginService, PluginServiceError


def choose_only_pair(devices):
    if len(devices) != 2:
        raise PluginServiceError(
            "launcher apps require exactly two Easy-Switch devices; "
            f"found {len(devices)}"
        )
    return devices[0], devices[1]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or argv[0] not in {"0", "1", "2"}:
        print("usage: app_launcher.py {0,1,2}", file=sys.stderr)
        return 2
    host = int(argv[0])
    try:
        with PluginService(timeout=3.0) as service:
            first, second = choose_only_pair(service.devices())
            service.switch_pair(first["id"], second["id"], host)
    except (OSError, PluginServiceError, TimeoutError) as error:
        print(f"The Mouse Is Coming Too failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
