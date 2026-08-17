from typing import List, Set, Protocol
from queue import Queue
from threading import Thread, Lock


class LinkProvider(Protocol):
    def get_links(self, url: str) -> List[str]:
        ...


def crawl_same_host_concurrent(
    start_url: str,
    provider: LinkProvider,
    num_workers: int
) -> Set[str]:

    hostname = get_hostname(start_url)

    queue = Queue()
    visited = set()
    lock = Lock()

    queue.put(start_url)
    visited.add(start_url)

    def worker():
        while True:
            url = queue.get()

            if url is None:
                queue.task_done()
                break

            try:
                for link in provider.get_links(url):
                    if get_hostname(link) != hostname:
                        continue

                    with lock:
                        if link in visited:
                            continue
                        visited.add(link)

                    queue.put(link)
            finally:
                queue.task_done()

    workers = [Thread(target=worker) for _ in range(num_workers)]

    for t in workers:
        t.start()

    # Wait until every discovered URL has been processed.
    queue.join()

    # Stop workers.
    for _ in workers:
        queue.put(None)

    for t in workers:
        t.join()

    return visited
