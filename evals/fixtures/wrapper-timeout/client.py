class Client:
    def __init__(self, transport, default_timeout=30):
        self.transport = transport
        self.default_timeout = default_timeout

    def get(self, url, timeout=None):
        effective_timeout = timeout or self.default_timeout
        return self.transport.request("GET", url, timeout=effective_timeout)
