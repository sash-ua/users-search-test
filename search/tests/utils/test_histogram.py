from io import StringIO
import sys

from search.utils.histogram import print_distance_histogram


def capture_print(fn, *args, **kwargs) -> str:
    buf = StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        fn(*args, **kwargs)
    finally:
        sys.stdout = old
    return buf.getvalue()


def test_histogram_no_distances():
    out = capture_print(print_distance_histogram, [])
    assert "No distances to summarize." in out


def test_histogram_all_equal():
    out = capture_print(print_distance_histogram, [0.5, 0.5, 0.5])
    assert "Distances all equal: 0.5000" in out


def test_histogram_bins():
    out = capture_print(print_distance_histogram, [0.1, 0.2, 0.8, 0.9], bins=4)
    assert "Distance histogram (top-k):" in out
    # Should print 4 bin lines
    assert out.strip().count("\n") >= 4

