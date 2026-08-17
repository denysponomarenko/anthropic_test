import threading


class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.head = None  # most recently used
        self.tail = None  # least recently used
        self.lock = threading.Lock()

    def _remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

    def _add_front(self, node):
        node.next = self.head
        node.prev = None

        if self.head:
            self.head.prev = node
        else:
            self.tail = node

        self.head = node

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None

            node = self.cache[key]
            self._remove(node)
            self._add_front(node)

            return node.value

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                node.value = value
                self._remove(node)
                self._add_front(node)
                return

            node = Node(key, value)
            self.cache[key] = node
            self._add_front(node)

            if len(self.cache) > self.capacity:
                lru = self.tail
                self._remove(lru)
                del self.cache[lru.key]

    def delete(self, key):
        with self.lock:
            if key not in self.cache:
                return False

            node = self.cache[key]
            self._remove(node)
            del self.cache[key]
            return True

    def size(self):
        with self.lock:
            return len(self.cache)
