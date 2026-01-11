import curses
import time


def main(w):
    w.clear()
    times = [0 for i in range(20)]
    key = 'key'
    w.addstr(0, 0, "tap any key (or q to quit)")
    while key not in "q":
        key = w.getkey()
        curses.flash()
        w.clear()
        times = update_times(times)
        w.addstr(0, 0, f"  no smoothing: {bpm(delta(times, 2)):.2f}")
        w.addstr(1, 0, f" 4 tap average: {bpm(delta(times, 4)):.2f}")
        w.addstr(2, 0, f" 8 tap average: {bpm(delta(times, 8)):.2f}")
        w.addstr(3, 0, f"12 tap average: {bpm(delta(times, 12)):.2f}")
        w.addstr(4, 0, f"16 tap average: {bpm(delta(times, 16)):.2f}")
        print_history(w, times, 10)
        print_times(w, times, 11)
    print(bpm)


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


def print_times(w, times, row):
    for i in range(len(times)):
        w.addstr(row + i, 20, f"{times[i]:.2f}")


def print_history(w, times, row):
    for i in range(1, len(times)):
        w.addstr(row + i, 0, f"{bpm(times[i - 1] - times[i]):.2f}")


curses.wrapper(main)


# press a number to change averaging
# show variance, precision
