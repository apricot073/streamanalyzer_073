from collections import Counter


class Stats:
    def __init__(self):
        self.total = 0
        self.by_level = Counter()
        self.by_source = Counter()
        self.error_sources = Counter()  # только ERROR и CRITICAL
        self.first_ts = None
        self.last_ts = None
        self.skipped = 0

    def add(self, event):
        """Учесть одно событие."""
        self.total += 1
        self.by_level[event.level] += 1
        self.by_source[event.source] += 1
        if event.level.is_error():
            self.error_sources[event.source] += 1
        if self.first_ts is None or event.timestamp < self.first_ts:
            self.first_ts = event.timestamp
        if self.last_ts is None or event.timestamp > self.last_ts:
            self.last_ts = event.timestamp

    def top_error_sources(self, n=5):
        """Топ-5 источников ошибок по убыванию, при равенстве - по имени."""
        return self.error_sources.most_common(n)
