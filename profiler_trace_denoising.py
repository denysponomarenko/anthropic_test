from typing import List, Tuple


Sample = Tuple[int, List[str]]
Event = Tuple[str, int, str]


def denoise_profiler_trace(
    samples: List[Sample],
    n: int,
) -> List[Event]:
    """
    Convert sampled stacks into denoised start/end events.

    A frame is emitted only after appearing at the same stack depth
    with the same function name for n consecutive samples.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    events: List[Event] = []

    # For each stack depth, track the currently observed candidate:
    # (function_name, consecutive_count, confirmed)
    #
    # We use depth as the identity because recursive calls can have
    # the same function name at different depths.
    candidate = {}  # depth -> [name, count, confirmed]

    previous_stack: List[str] = []

    for timestamp, stack in samples:
        max_depth = max(len(previous_stack), len(stack))

        ended = []
        started = []

        for depth in range(max_depth):
            old_name = previous_stack[depth] if depth < len(previous_stack) else None
            new_name = stack[depth] if depth < len(stack) else None

            state = candidate.get(depth)

            # Same frame as the previous sample.
            if new_name is not None and new_name == old_name:
                if state is None or state[0] != new_name:
                    state = [new_name, 1, False]
                    candidate[depth] = state
                else:
                    state[1] += 1

                # Candidate has now survived n samples.
                if not state[2] and state[1] >= n:
                    state[2] = True
                    started.append((depth, new_name))

            else:
                # The previous candidate is disappearing/replaced.
                if state is not None and state[2]:
                    ended.append((depth, state[0]))

                if new_name is not None:
                    # New candidate starts with this sample.
                    candidate[depth] = [new_name, 1, False]
                else:
                    candidate.pop(depth, None)

        # End events: deepest -> shallowest.
        for depth, name in sorted(ended, reverse=True):
            events.append(("end", timestamp, name))

        # Start events: shallowest -> deepest.
        for depth, name in sorted(started):
            events.append(("start", timestamp, name))

        previous_stack = stack

    return events
