import curses
import time
from threading import Thread, Lock
from math import fmod


"""
a keypress, after updating the data, starts the drawing thread
the drawing thread accesses tap count but doesn't modify it
after starting, only the drawing thread draws

the main thread must be the one taking input
main thread changes the tap count, which the draw thread listens to
once draw thread

"""

text_width = 30
tap_width = 20


def main(w):
    define_colors()
    lock = Lock()
    text_w = curses.newwin(15, text_width, 0, 0)
    tap_w = curses.newwin(20, 20, 0, text_width)

    global tap_count
    tap_count = 1
    times = [0 for i in range(512)]
    intervals = [2, 4, 8, 12, 16, 32, 42, 69, 100, 128, 192, 256, 420, 512]

    w.clear()
    text_w.addstr(2, 2, "tap any key (or q to quit)")
    key = text_w.getkey()

    draw_thread = Thread(target=draw, args=[tap_w, lock])
    draw_thread.start()
    while key != "q" and key != "\x1b":
        key = text_w.getkey()
        text_w.clear()
        times = update_times(times)
        text_w.addstr(2, 2, "average of the last...")
        for i in range(len(intervals)):
            if bpm(delta(times, intervals[i])):
                text_w.addstr(i + 4, 4, f"{intervals[i]:>3} taps: {
                    bpm(delta(times, intervals[i])):.2f}")
        text_w.noutrefresh()
        curses.doupdate()
        with lock:
            tap_count += 1
    with lock:
        tap_count = 0
    draw_thread.join(3)


def define_colors():
    global blue, gray, red
    curses.curs_set(0)
    curses.use_default_colors()
    curses.init_pair(39, 39, -1)
    curses.init_pair(111, 111, -1)
    curses.init_pair(127, 127, -1)
    blue = curses.color_pair(39)
    gray = curses.color_pair(111)
    red = curses.color_pair(127)


def draw(w, lock):
    global tap_count
    local_count = 0
    while True:
        with lock:
            if tap_count == 0:
                break
        draw_tap(w, local_count)
        w.noutrefresh()
        curses.doupdate()
        time.sleep(1)
        local_count += 1


def draw_tap(w, tap_count):
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
    x = 0
    y = 2

    w.addstr(y, x, tap.split("\n")[y], red)
    y += 1
    while y < len(tap.split("\n")):
        w.addstr(y, x, tap.split("\n")[y], gray)
        y += 1
    if tap_count < tap_rotate_end:
        w.addstr(1, x + 7, handle(tap_count), red)
    else:
        w.addstr(1, x + 7, handle(tap_rotate_end), red)
    for i in range(tap_count - stream_start):
        w.addstr(y, x + 2, water[mod2(tap_count + mod2(y))], blue)
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
