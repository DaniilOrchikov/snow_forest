def animation_generator(arr, step):
    v = 0
    ln = len(arr) * step
    while True:
        yield arr[v // step]
        v += 1
        v %= ln


class Animation:
    def __init__(self, arr, step=10):
        self.generator = animation_generator(arr, step)
        self.width, self.height = arr[0].get_size()

    def next(self):
        return next(self.generator)
