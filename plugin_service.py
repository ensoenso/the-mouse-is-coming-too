"""Narrow interoperability client for the local Logitech Plugin Service.

The client can discover devices offered by the installed two-device
Easy-Switch action and invoke only that action. It uses no debugger, external
dependency, credential, persistent connection, or automatic execution retry.
"""
from __future__ import annotations

import json
import math
import socket
import struct
import time
from typing import Any

SOCKET_PATH = "/tmp/LogiPluginService"
MAX_FRAME = 16 * 1024 * 1024
EASY_SWITCH_ACTION = "$@Generic___@EasySwitch2"


class PluginServiceError(RuntimeError):
    pass


def checksum(data: bytes) -> int:
    value = 3074457345618258791
    for byte in data:
        value = ((value + byte) * 3074457345618258799) & ((1 << 64) - 1)
    return value


def frame(channel: str, message: dict[str, Any]) -> bytes:
    payload = json.dumps(message, separators=(",", ":")).encode("utf-8")
    encoded_channel = channel.encode("ascii")
    if not encoded_channel or len(encoded_channel) > 255:
        raise PluginServiceError("invalid channel length")
    header = b"LogiConn\x01\x00\x00" + bytes([len(encoded_channel)]) + encoded_channel
    header += struct.pack("<I", len(payload))
    body = header + struct.pack("<Q", checksum(header))
    body += payload + struct.pack("<Q", checksum(payload))
    if len(body) > MAX_FRAME:
        raise PluginServiceError("request exceeds frame size limit")
    return struct.pack("<I", len(body)) + body


def decode_body(body: bytes) -> dict[str, Any]:
    if len(body) < 32 or body[:11] != b"LogiConn\x01\x00\x00":
        raise PluginServiceError("invalid protocol header")
    offset = 12 + body[11]
    if offset + 20 > len(body):
        raise PluginServiceError("truncated protocol header")
    payload_size = struct.unpack_from("<I", body, offset)[0]
    header_end = offset + 4
    if len(body) != header_end + 16 + payload_size:
        raise PluginServiceError("invalid payload size")
    if checksum(body[:header_end]) != struct.unpack_from("<Q", body, header_end)[0]:
        raise PluginServiceError("invalid header checksum")
    payload = body[header_end + 8:-8]
    if checksum(payload) != struct.unpack_from("<Q", body, len(body) - 8)[0]:
        raise PluginServiceError("invalid payload checksum")
    try:
        message = json.loads(payload)
        channel = body[12:offset].decode("ascii")
    except (ValueError, UnicodeError) as error:
        raise PluginServiceError("invalid message encoding") from error
    if not isinstance(message, dict) or message.get("channelName") != channel:
        raise PluginServiceError("invalid message or mismatched channel")
    return message


class PluginService:
    def __init__(self, timeout: float = 3.0, socket_path: str = SOCKET_PATH):
        if not math.isfinite(timeout) or timeout <= 0:
            raise PluginServiceError("timeout must be a positive finite number")
        self.timeout = timeout
        self.next_id = 1
        self.events: list[dict[str, Any]] = []
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.socket.settimeout(timeout)
            self.socket.connect(socket_path)
        except OSError as error:
            self.socket.close()
            raise PluginServiceError(
                f"cannot connect to {socket_path}: {error}. "
                "Logi Options+ and its Plugin Service must be running normally."
            ) from error

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.socket.close()

    def _remaining(self, deadline: float) -> None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Plugin Service request timed out")
        self.socket.settimeout(remaining)

    def _read_exact(self, count: int, deadline: float) -> bytes:
        data = bytearray()
        while len(data) < count:
            self._remaining(deadline)
            part = self.socket.recv(count - len(data))
            if not part:
                raise PluginServiceError("Plugin Service closed the connection")
            data.extend(part)
        return bytes(data)

    def receive(self, deadline: float) -> dict[str, Any]:
        size = struct.unpack("<I", self._read_exact(4, deadline))[0]
        if not 32 <= size <= MAX_FRAME:
            raise PluginServiceError(f"invalid frame size {size}")
        return decode_body(self._read_exact(size, deadline))

    def request(self, channel: str, name: str, parameters=None, data=None,
                *, allow_failure=False) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        message = {"id": request_id, "messageType": "Request", "channelName": channel,
                   "name": name, "parameters": parameters or {}}
        if data is not None:
            message["data"] = data
        deadline = time.monotonic() + self.timeout
        self._remaining(deadline)
        self.socket.sendall(frame(channel, message))
        while True:
            response = self.receive(deadline)
            if response.get("messageType") == "Event":
                # Only retain switch events, not unrelated personal/account state.
                if response.get("channelName") == "easySwitch":
                    self.events.append(response)
                    self.events = self.events[-64:]
                continue
            if (response.get("id") != request_id
                    or response.get("channelName") != channel
                    or response.get("messageType") != "Response"):
                continue
            if response.get("failed") is not False:
                if not allow_failure:
                    raise PluginServiceError(
                        f"{name}: {response.get('errorMessage', 'unsuccessful response')}"
                    )
            return response

    def devices(self) -> list[dict[str, Any]]:
        response = self.request("configui", "GetProfileActionListboxItems",
                                {"actionName": EASY_SWITCH_ACTION, "controlName": "device"}, {})
        items = response.get("data", {}).get("items")
        if not isinstance(items, list):
            raise PluginServiceError("unexpected Easy-Switch device list")
        return [{"id": item["name"], "modelId": item["name"],
                 "displayName": item["displayName"]} for item in items]

    def switch_pair(self, first: str, second: str, host: int) -> float:
        """Wait for both outgoing events, NOT hardware acknowledgements."""
        if first == second or not first or not second or host not in (0, 1, 2):
            raise PluginServiceError("two distinct devices and a host in 0..2 are required")
        # Any request registers this connection for channel broadcasts. This
        # deliberately unknown request is harmless and changes no service state.
        self.request("easySwitch", "DiagnosticReadOnlyProbe", allow_failure=True)
        self.events.clear()
        params = {}
        for suffix, device_id in (("", first), ("2", second)):
            params.update({f"device{suffix}": device_id, f"deviceId{suffix}": device_id,
                           f"channel{suffix}": str(host), f"channelId{suffix}": str(host)})
        started = time.monotonic()
        try:
            self.request("pluginManagement", "ExecuteAction",
                         {"actionName": EASY_SWITCH_ACTION, "numberOfTicks": 0},
                         {"actionParameters": params})
            pending = {first, second}
            deadline = started + self.timeout
            while pending:
                event = self.events.pop(0) if self.events else self.receive(deadline)
                if (event.get("messageType") == "Event"
                        and event.get("channelName") == "easySwitch"
                        and event.get("name") == "TriggerEasySwitch"):
                    data = event.get("data") or {}
                    if data.get("channel") == host:
                        pending.discard(data.get("deviceId"))
        except (OSError, PluginServiceError) as error:
            raise PluginServiceError(
                f"execution outcome uncertain: {error}. Do not retry automatically; "
                "one or both devices may already have switched."
            ) from error
        return time.monotonic() - started
