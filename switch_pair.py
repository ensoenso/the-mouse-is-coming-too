#!/usr/bin/env python3
"""Inspect or switch the device pair exposed by Options+ on this Mac."""
from __future__ import annotations

import argparse
import json
import sys

from plugin_service import PluginService, PluginServiceError


class PairSelectionError(RuntimeError):
    pass


def find_device(devices, selector):
    wanted = selector.casefold()
    exact = [
        item
        for item in devices
        if wanted
        in {
            str(item.get("id", "")).casefold(),
            str(item.get("displayName", "")).casefold(),
        }
    ]
    if len(exact) == 1:
        return exact[0]
    partial = [
        item
        for item in devices
        if wanted in str(item.get("displayName", "")).casefold()
    ]
    if len(partial) == 1:
        return partial[0]
    if not exact and not partial:
        raise PairSelectionError(f"no action-compatible device matches {selector!r}")
    raise PairSelectionError(f"device selector {selector!r} is ambiguous")


def choose_pair(devices, first=None, second=None):
    if first is None and second is None:
        if len(devices) != 2:
            raise PairSelectionError(
                "automatic selection requires exactly two action-compatible "
                f"devices; found {len(devices)}"
            )
        return devices[0], devices[1]
    if first is None or second is None:
        raise PairSelectionError("--first and --second must be supplied together")
    selected = find_device(devices, first), find_device(devices, second)
    if selected[0]["id"] == selected[1]["id"]:
        raise PairSelectionError("the selectors resolve to the same device")
    return selected


def command_status(args):
    with PluginService(args.timeout) as service:
        print(json.dumps(service.devices(), indent=2))


def command_switch(args):
    with PluginService(args.timeout) as service:
        first, second = choose_pair(service.devices(), args.first, args.second)
        label = f"{first['displayName']} and {second['displayName']}"
        if not args.execute:
            print(f"Dry run: would switch {label} to host {args.host}.")
            print("Re-run with --execute to send the command.")
            return
        elapsed = service.switch_pair(first["id"], second["id"], args.host - 1)
        print(f"Sent both switch commands for {label} ({elapsed:.3f}s).")
        print("Device reconnection is not confirmed by this response.")


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--timeout", type=float, default=3.0)
    commands = result.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status", help="list action-compatible devices")
    status.set_defaults(function=command_status)
    switch = commands.add_parser("switch", help="switch two devices to a host")
    switch.add_argument("host", type=int, choices=(1, 2, 3))
    switch.add_argument("--first")
    switch.add_argument("--second")
    switch.add_argument("--execute", action="store_true")
    switch.set_defaults(function=command_switch)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        args.function(args)
    except (OSError, PairSelectionError, PluginServiceError, TimeoutError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
