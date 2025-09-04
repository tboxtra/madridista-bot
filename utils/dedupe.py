from collections import deque

class DeDupe:
    def __init__(self, maxlen: int = 200):
        self.seen = set()
        self.order = deque(maxlen=maxlen)

    def is_new(self, key: str) -> bool:
        if key in self.seen:
            return False
        self.seen.add(key)
        self.order.append(key)
        if len(self.order) == self.order.maxlen:
            # trim old from set
            while len(self.seen) > self.order.maxlen:
                old = self.order.popleft()
                self.seen.discard(old)
        return True
