import curses
import time
from math import fmod


def main(w):
    w.clear()
    curses.curs_set(0)
    curses.use_default_colors()
    curses.init_pair(39, 39, -1)
    curses.init_pair(111, 111, -1)
    curses.init_pair(127, 127, -1)
    blue = curses.color_pair(39)
    grey = curses.color_pair(111)
    red = curses.color_pair(127)
    times = [0 for i in range(512)]
    taps = 0
    intervals = [2, 4, 8, 12, 16, 32, 42, 69, 100, 128, 192, 256, 420, 512]
    key = 'key'
    w.addstr(2, 2, "tap any key (or q to quit)")
    while key not in "q" and key != "\x1b":
        key = w.getkey()
        # curses.flash()
        w.clear()
        times = update_times(times)
        w.addstr(2, 2, "average of the last...")
        for i in range(len(intervals)):
            if bpm(delta(times, intervals[i])):
                w.addstr(i + 4, 4, f"{intervals[i]:>3} taps: {
                         bpm(delta(times, intervals[i])):.2f}")
        taps += 1
        draw_tap(w, taps, blue, red, grey)


def draw_tap(w, taps, blue, red, gray):
    tap = """

         H
        {|}
 ,#############
 #
 #   ..........
[_____]"""
    water = ["\\\\\\", "///"]
    tap_rotate_end = 30
    stream_start = 7
    stream_length = 4
    x = 28
    y = 2

    w.addstr(y, x, tap.split("\n")[y], red)
    y += 1
    while y < len(tap.split("\n")):
        w.addstr(y, x, tap.split("\n")[y], gray)
        y += 1
    if taps < tap_rotate_end:
        w.addstr(1, x + 7, handle(taps), red)
    else:
        w.addstr(1, x + 7, handle(tap_rotate_end), red)
    for i in range(taps - stream_start):
        w.addstr(y, x + 2, water[mod2(taps + mod2(y))], blue)
        y += 1
        if i > stream_length:
            break


def handle(taps):
    handle = ["o-==O", "0-=-0", "O==-o", " O>o ", "  O  ", " o<O "]
    return handle[int(fmod(taps, len(handle)))]


def mod2(i):
    return int(fmod(i, 2))


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
