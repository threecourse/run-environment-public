import random


class Model:

    def calc(self, n, outer=1000000):
        m = 1000000009
        a = 1000000007
        x = random.randint(0, m)
        for o in range(outer):
            for i in range(n):
                x *= a
                x %= m
        return float(x) / m
