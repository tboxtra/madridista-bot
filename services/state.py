from collections import deque

class DeDupe:
    def __init__(self, maxlen: int = 400):
        self.q = deque(maxlen=maxlen)
        self.seen = set()
    def new(self, key: str) -> bool:
        if key in self.seen:
            return False
        self.seen.add(key)
        self.q.append(key)
        while len(self.seen) > self.q.maxlen:
            old = self.q.popleft()
            self.seen.discard(old)
        return True
