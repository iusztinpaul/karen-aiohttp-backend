class Worker:

    def __init__(self, work_handler, *args, **kwargs):
        self.work_handler = work_handler

    def work(self, data):
        return self.work_handler.handle(data)


class Person(Worker):

    def __init__(self, work_handler, name, *args, **kwargs):
        self.name = name
        super().__init__(work_handler, *args, **kwargs)

    def work(self, chair):
        chair = super().work(chair)
        print("{}: {}".format(self.name, chair))

        return chair
