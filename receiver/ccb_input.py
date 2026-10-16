import threading

class Writer:
    def __init__(self, pipe, data):
        self.pipe = pipe
        self.data = data
        self.error = None
        self.thread = threading.Thread(target=self.write)

    def write(self):
        try:
            self.pipe.write(self.data)
            self.pipe.flush()
        except (BrokenPipeError, OSError) as exc:
            self.error = exc
        finally:
            self.pipe.close()

    def start(self):
        self.thread.start()

    def finish(self):
        self.thread.join(timeout=3)
        if self.thread.is_alive():
            raise RuntimeError("Input writer still running")
        return self.error
