import os
import hashlib
from collections import defaultdict


def find_duplicates(root: str) -> list[list[str]]:
    # First group by file size
    by_size = defaultdict(list)

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # Ignore symlinked directories
        dirnames[:] = [
            d for d in dirnames
            if not os.path.islink(os.path.join(dirpath, d))
        ]

        for filename in filenames:
            path = os.path.join(dirpath, filename)

            # Ignore symlinked files
            if os.path.islink(path):
                continue

            size = os.path.getsize(path)
            by_size[size].append(path)

    # Only files with the same size can be duplicates
    duplicates = []

    for paths in by_size.values():
        if len(paths) < 2:
            continue

        by_hash = defaultdict(list)

        for path in paths:
            h = hashlib.sha256()

            with open(path, "rb") as f:
                while chunk := f.read(1024 * 1024):  # 1 MB at a time
                    h.update(chunk)

            by_hash[h.digest()].append(path)

        for group in by_hash.values():
            if len(group) >= 2:
                duplicates.append(group)

    return duplicates
