from threading import Thread


class Filter(Thread):
    default_class = None

    def __init__(self, worker, input_pipe=None, output_pipe=None, *args):
        super().__init__()

        if self.default_class is None and input_pipe is None:
            raise AssertionError('default_class and input_pipe cannot be null at the same time')

        self.input_pipe = input_pipe
        self.output_pipe = output_pipe
        self.worker = worker
        self.default_class_args = args
        self.run_loop = True

    def run(self):
        self.run_loop = True

        while self.run_loop:
            if self.input_pipe:
                data = self.input_pipe.get_data()
            else:
                data = self.default_class(*self.default_class_args)

            try:
                data = self.worker.work(data)
            except:
                # If there are any problems add the data back into the pipe and start from scratch.
                if self.input_pipe is not None:
                    self.input_pipe.put_data(data)

                continue

            if self.output_pipe is not None:
                self.output_pipe.put_data(data)
            else:
                print("Output pipe to stdo: {}".format(data))

            a = 2

    def filter(self):
        super().start()

    def stop(self):
        self.run_loop = False
