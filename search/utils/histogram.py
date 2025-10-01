from typing import List


def print_distance_histogram(distances: List[float], bins: int = 8) -> None:
    if not distances:
        print("No distances to summarize.")
        return
    dmin, dmax = min(distances), max(distances)
    if dmin == dmax:
        print(f"Distances all equal: {dmin:.4f}")
        return
    step = (dmax - dmin) / bins
    counts = [0] * bins
    for d in distances:
        idx = int((d - dmin) / step)
        if idx == bins:
            idx -= 1
        counts[idx] += 1
    print("Distance histogram (top-k):")
    for i, c in enumerate(counts):
        start = dmin + i * step
        end = start + step
        bar = "#" * c
        print(f"  {start:.2f}–{end:.2f}: {c} {bar}")
