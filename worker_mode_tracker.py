from collections import Counter


class WorkerFrequencyCoordinator:
    def __init__(self, num_workers: int):
        self.active = [True] * num_workers
        self.worker_data = [Counter() for _ in range(num_workers)]
        self.global_freq = Counter()

    def addData(self, worker_id: int, values: list[int]) -> None:
        if not self.active[worker_id]:
            return

        for value in values:
            self.worker_data[worker_id][value] += 1
            self.global_freq[value] += 1

    def removeWorker(self, worker_id: int) -> bool:
        if not self.active[worker_id]:
            return False

        # Remove this worker's contribution from global counts.
        for value, count in self.worker_data[worker_id].items():
            self.global_freq[value] -= count

            if self.global_freq[value] == 0:
                del self.global_freq[value]

        self.worker_data[worker_id].clear()
        self.active[worker_id] = False

        return True

    def findMode(self) -> int:
        if not self.global_freq:
            return -1

        # Highest frequency, then smallest value.
        return min(
            self.global_freq,
            key=lambda value: (-self.global_freq[value], value)
        )

    def topKFrequent(self, k: int) -> list[int]:
        values = list(self.global_freq.keys())

        values.sort(
            key=lambda value: (-self.global_freq[value], value)
        )

        return values[:k]
