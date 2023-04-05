class LamportClock:
    def __init__(self):
        self.time = 0

    def increment(self):
        self.time += 1

    def update(self, time):
        self.time = max(self.time, time) + 1

    def get_time(self):
        return self.time
