class RecordStore:
    def __init__(self):
        # key -> field -> list of (start_time, value, expire_time)
        self.data = {}

    def set(self, timestamp, key, field, value):
        self.data.setdefault(key, {}).setdefault(field, []).append(
            (timestamp, value, None)
        )
        return ""

    def get(self, timestamp, key, field):
        item = self._get_at(timestamp, key, field)
        return item[0] if item else ""

    def compare_and_set(self, timestamp, key, field, expected, value):
        current = self._get_at(timestamp, key, field)

        if not current or current[0] != expected:
            return "false"

        self.data[key][field].append((timestamp, value, None))
        return "true"

    def compare_and_delete(self, timestamp, key, field, expected):
        current = self._get_at(timestamp, key, field)

        if not current or current[0] != expected:
            return "false"

        # None value means deleted
        self.data[key][field].append((timestamp, None, None))
        return "true"

    def scan(self, timestamp, key):
        return self.scan_by_prefix(timestamp, key, "")

    def scan_by_prefix(self, timestamp, key, prefix):
        if key not in self.data:
            return ""

        result = []

        for field in sorted(self.data[key]):
            if not field.startswith(prefix):
                continue

            item = self._get_at(timestamp, key, field)

            if item and item[0] is not None:
                result.append(f"{field}({item[0]})")

        return ", ".join(result)

    def set_with_ttl(self, timestamp, key, field, value, ttl):
        self.data.setdefault(key, {}).setdefault(field, []).append(
            (timestamp, value, timestamp + ttl)
        )
        return ""

    def get_at(self, timestamp, key, field, at_timestamp):
        item = self._get_at(at_timestamp, key, field)
        return item[0] if item else ""

    def _get_at(self, timestamp, key, field):
        if key not in self.data or field not in self.data[key]:
            return None

        history = self.data[key][field]

        for start, value, expire in reversed(history):
            if start > timestamp:
                continue

            if value is None:
                return None

            if expire is not None and timestamp >= expire:
                return None

            return value, expire

        return None
