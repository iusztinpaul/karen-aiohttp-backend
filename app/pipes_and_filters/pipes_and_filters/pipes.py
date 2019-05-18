from multiprocessing import Queue


class Pipe:
    QUEUE_MAX_SIZE = 500

    def __init__(self):
        self.buffer = Queue(self.QUEUE_MAX_SIZE)

    def is_put_ready(self):
        return not self.buffer.full()

    def is_get_ready(self):
        return not self.buffer.empty()

    def get_data(self):
        return self.buffer.get(True)

    def put_data(self, data):
        self.buffer.put(data, True)

    def clear(self):
        self.buffer.empty()
