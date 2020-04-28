
class WatchStr:

    def __init__(self, value, callback):
        self.value = value
        self.callback = callback

    def update(self, value):
        self.value = value
        self.callback()

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value, self.callback

class WatchNumber:

    def __init__(self, x, callback, base=10):
        self.callback = callback
        super().__init__(x, base=base)

    def update(self, value):
        self.value = value
        self.callback()

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value, self.callback

class WatchBool:

    def __init__(self, value: bool, callback):
        self.value = value
        self.callback = callback

    def update(self, value: bool):
        self.value = value
        self.callback()

    def __nonzero__(self):
        return self.value == True

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value, self.callback