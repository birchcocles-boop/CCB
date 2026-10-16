import threading

class Collector:
    def __init__(self, pipe, limit):
        self.data = bytearray()
        self.limit = limit
        self.truncated = False
        self.thread = threading.Thread(
            target=self.drain, args=(pipe,), daemon=True
        )

    def drain(self, pipe):
        for chunk in iter(lambda: pipe.read(4096), b""):
            room = max(0, self.limit - len(self.data))
            self.data.extend(chunk[:room])
            self.truncated |= len(chunk) > room

    def start(self):
        self.thread.start()

    def finish(self):
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise RuntimeError("Output collector still running")
        return bytes(self.data), self.truncated
