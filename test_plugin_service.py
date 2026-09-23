import struct
import unittest
from unittest.mock import patch

from plugin_service import (
    MAX_FRAME,
    PluginService,
    PluginServiceError,
    decode_body,
    frame,
)


def response(request_id=1, channel="core", **extra):
    return {
        "id": request_id,
        "channelName": channel,
        "messageType": "Response",
        "failed": False,
        "data": True,
        **extra,
    }


def event(device, channel=1):
    return {
        "id": 0,
        "channelName": "easySwitch",
        "messageType": "Event",
        "name": "TriggerEasySwitch",
        "data": {"deviceId": device, "channel": channel},
    }


class FakeSocket:
    def __init__(self, messages=(), raw=None):
        self.data = bytearray(
            raw
            if raw is not None
            else b"".join(frame(item["channelName"], item) for item in messages)
        )
        self.sent = []
        self.closed = False

    def settimeout(self, _):
        pass

    def connect(self, _):
        pass

    def close(self):
        self.closed = True

    def recv(self, count):
        count = min(count, 3)
        result = bytes(self.data[:count])
        del self.data[:count]
        return result

    def sendall(self, data):
        self.sent.append(decode_body(data[4:]))


class ProtocolTests(unittest.TestCase):
    def test_roundtrip_unicode(self):
        message = response(data={"label": "Clavier é"})
        wire = frame("core", message)
        self.assertEqual(len(wire) - 4, struct.unpack("<I", wire[:4])[0])
        self.assertEqual(message, decode_body(wire[4:]))

    def test_corrupt_header_is_rejected(self):
        body = bytearray(frame("core", response())[4:])
        body[12] ^= 1
        with self.assertRaisesRegex(PluginServiceError, "header checksum"):
            decode_body(body)

    def test_corrupt_payload_is_rejected(self):
        body = bytearray(frame("core", response())[4:])
        body[-9] ^= 1
        with self.assertRaisesRegex(PluginServiceError, "payload checksum"):
            decode_body(body)

    def test_invalid_frame_size_is_rejected(self):
        fake = FakeSocket(raw=struct.pack("<I", MAX_FRAME + 1))
        with patch("plugin_service.socket.socket", return_value=fake):
            with PluginService() as client:
                with self.assertRaisesRegex(PluginServiceError, "frame size"):
                    client.request("core", "GetServiceStatus")
        self.assertTrue(fake.closed)

    def test_response_matching_with_fragmented_reads(self):
        fake = FakeSocket([response(9), event("mouse"), response(data="correct")])
        with patch("plugin_service.socket.socket", return_value=fake):
            with PluginService() as client:
                self.assertEqual(
                    "correct", client.request("core", "GetServiceStatus")["data"]
                )
                self.assertEqual(1, len(client.events))

    def test_switch_waits_for_both_events(self):
        fake = FakeSocket(
            [
                response(channel="easySwitch", failed=True),
                event("mouse"),
                response(2, "pluginManagement"),
                event("keys"),
            ]
        )
        with patch("plugin_service.socket.socket", return_value=fake):
            with PluginService() as client:
                self.assertGreaterEqual(client.switch_pair("mouse", "keys", 1), 0)
        self.assertEqual(2, len(fake.sent))
        parameters = fake.sent[1]["data"]["actionParameters"]
        self.assertEqual("mouse", parameters["deviceId"])
        self.assertEqual("keys", parameters["deviceId2"])
        self.assertEqual("1", parameters["channelId2"])

    def test_missing_event_is_never_retried(self):
        fake = FakeSocket(
            [
                response(channel="easySwitch", failed=True),
                response(2, "pluginManagement"),
                event("mouse"),
                event("keys", 0),
            ]
        )
        with patch("plugin_service.socket.socket", return_value=fake):
            with PluginService() as client:
                with self.assertRaisesRegex(PluginServiceError, "outcome uncertain"):
                    client.switch_pair("mouse", "keys", 1)
        self.assertEqual(2, len(fake.sent))


if __name__ == "__main__":
    unittest.main()
