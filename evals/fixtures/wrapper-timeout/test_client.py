import unittest

from client import Client


class RecordingTransport:
    def __init__(self):
        self.calls = []

    def request(self, method, url, timeout):
        self.calls.append((method, url, timeout))
        return {"ok": True}


class ClientTests(unittest.TestCase):
    def test_uses_default_when_timeout_is_omitted(self):
        transport = RecordingTransport()
        Client(transport, default_timeout=15).get("/health")
        self.assertEqual(transport.calls[-1][2], 15)

    def test_zero_disables_transport_timeout(self):
        transport = RecordingTransport()
        Client(transport, default_timeout=15).get("/stream", timeout=0)
        self.assertEqual(transport.calls[-1][2], 0)


if __name__ == "__main__":
    unittest.main()
