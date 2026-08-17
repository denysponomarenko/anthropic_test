from typing import List, Tuple

def stack_events(
    profiles: List[Tuple[int, List[str]]]
) -> List[Tuple[str, int, str]]:
    events = []

    for i, (timestamp, stack) in enumerate(profiles):
        prev = profiles[i - 1][1] if i > 0 else []

        # End events: deepest -> shallowest
        for depth in range(len(prev) - 1, len(stack) - 1, -1):
            events.append(("end", timestamp, prev[depth]))

        # Also handle changed frames at the same depth.
        # End old frames first, deepest -> shallowest.
        common = min(len(prev), len(stack))
        for depth in range(common - 1, -1, -1):
            if prev[depth] != stack[depth]:
                events.append(("end", timestamp, prev[depth]))

        # Start events: shallowest -> deepest
        for depth in range(common):
            if prev[depth] != stack[depth]:
                events.append(("start", timestamp, stack[depth]))

        # New deeper frames
        for depth in range(common, len(stack)):
            events.append(("start", timestamp, stack[depth]))

    return events
