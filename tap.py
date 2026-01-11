import curses
import time


def main(w):
    w.clear()
    times = [0 for i in range(10)]
    key = 'key'
    w.addstr(0, 0, "tap any key (or q to quit)")
    while key not in "q":
        key = w.getkey()
        curses.flash()
        w.clear()
        times = update_times(times)
        print_times(w, times, 2)
    print(bpm)


def bpm(delta):
    return (1 / delta) * 60 if delta else 0


def delta(times, smooth):
    """smooth is 0 for no averaging, 1 will use 3 time values, 2 uses 4..."""
    if times[smooth + 1] == 0:
        return 0
    total = 0
    for i in range(smooth + 1):
        total += times[i] - times[i + 1]
    return total / smooth


def update_times(times):
    for i in range(len(times) - 1, 0, -1):
        times[i] = times[i - 1]
    times[0] = time.time()
    return times


def print_times(w, times, row):
    for i in range(len(times)):
        w.addstr(row + i, 0, str(times[i]))


curses.wrapper(main)


# press a number to change averaging
# show variance, precision
