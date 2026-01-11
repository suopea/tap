import curses
import time


def main(w):
    w.clear()
    times = [0 for i in range(512)]
    intervals = [2, 4, 8, 12, 16, 32, 42, 69, 100, 128, 192, 256, 420, 512]
    key = 'key'
    w.addstr(2, 2, "tap any key (or q to quit)")
    while key not in "q":
        key = w.getkey()
        curses.flash()
        w.clear()
        times = update_times(times)
        w.addstr(2, 2, "average of the last...")
        for i in range(len(intervals)):
            if bpm(delta(times, intervals[i])):
                w.addstr(i + 4, 4, f"{intervals[i]:>3} taps: {
                         bpm(delta(times, intervals[i])):.2f}")


def bpm(delta):
    return (1 / delta) * 60 if delta else 0


def delta(times, taps):
    """taps is 2 for no averaging, 3 will use 3 time values, 4 uses 4..."""
    if times[taps - 1] == 0:
        return 0
    total = 0
    for i in range(taps - 1):
        total += times[i] - times[i + 1]
    return total / (taps - 1) if taps > 2 else total


def update_times(times):
    for i in range(len(times) - 1, 0, -1):
        times[i] = times[i - 1]
    times[0] = time.time()
    return times


curses.wrapper(main)
