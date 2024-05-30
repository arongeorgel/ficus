class Tick:
    high = 1
    low = 0
    open = .1
    close = .9

    def __init__(self, high):
        self.high = high

    def get_high(self):
        return 1


def get_sum(a, b):
    r = Tick(10)
    return a + b + r.high


print(get_sum(4, 5))