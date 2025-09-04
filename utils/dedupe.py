from collections import deque

class DeDupe:
    def __init__(self, maxlen: int = 400):
        self.order = deque(maxlen=maxlen)
        self.seen = set()

    def is_new(self, key: str) -> bool:
        if key in self.seen: return False
        self.seen.add(key)
        self.order.append(key)
        while len(self.seen) > self.order.maxlen:
            old = self.order.popleft()
            if old in self.seen:
                self.seen.remove(old)
        return True
