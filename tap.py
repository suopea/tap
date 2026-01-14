import curses
import time
from threading import Thread, Lock
from math import fmod
from random import randrange

text_width = 30
tap_width = 20
minimum_height = 25
stream_length = 8
sticky_beat_smoothing = 3


def main(w):
    define_colors()
    lock = Lock()
    text_w = curses.newwin(15, text_width, 0, 0)
    tap_w = curses.newwin(20, 20, 0, text_width)

    global tap_count, sticky_delta, last_tap_time
    tap_count = 1
    sticky_delta = 1
    last_tap_time = time.time()
    times = [0 for i in range(512)]
    intervals = [2, 4, 8, 12, 16, 32, 42, 69, 100, 128, 192, 256, 420, 512]

    ensure_large_enough_window(text_w, w)
    text_w.clear()
    text_w.addstr(2, 2, "tap any key (or q to quit)")
    key = text_w.getkey()
    while key == "KEY_RESIZE":
        key = text_w.getkey()

    draw_thread = Thread(target=draw, args=[tap_w, lock, w])
    draw_thread.start()
    while key != "q" and key != "\x1b":
        key = text_w.getkey()
        ensure_large_enough_window(text_w, w)
        text_w.clear()
        if key != "KEY_RESIZE":
            times = update_times(times)
        text_w.addstr(2, 2, "average of the last...")
        for i in range(len(intervals)):
            if bpm(delta(times, intervals[i])):
                text_w.addstr(i + 4, 4, f"{intervals[i]:>3} taps: {
                    bpm(delta(times, intervals[i])):.2f}")
        text_w.noutrefresh()
        curses.doupdate()
        if key != "KEY_RESIZE":
            with lock:
                tap_count += 1
                sticky_delta = get_sticky_delta(times)
                last_tap_time = time.time()
    with lock:
        tap_count = 0
    draw_thread.join(3)


def ensure_large_enough_window(w, whole):
    while window_is_too_small(whole):
        w.clear()
        w.addstr(0, 0, "window too small")
        w.noutrefresh()
        curses.doupdate()
        time.sleep(0.01)


def get_sticky_delta(times):
    time_count = len([i for i in times if i])
    if time_count > sticky_beat_smoothing:
        return delta(times, sticky_beat_smoothing)
    else:
        return delta(times, time_count)


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


def draw(w, lock, whole_window):
    global tap_count, sticky_delta
    local_count = 0
    countdown_length = 24
    dancing_to_own_beat = False
    stream = []
    for i in range(stream_length):
        stream.append('   ')
    while tap_count < 3:
        pass
    while True:
        while window_is_too_small(whole_window):
            w.clear()
            w.noutrefresh()
            curses.doupdate()
            time.sleep(0.001)
        with lock:
            if tap_count == 0:
                break
        draw_tap(w, local_count, dancing_to_own_beat, stream)
        w.noutrefresh()
        curses.doupdate()
        if dancing_to_own_beat:
            if local_count > 0:
                local_count += -1
            if unexpected_tap_arrived(lock):
                dancing_to_own_beat = False
        else:
            local_count += 1
            if expected_tap_arrived(lock):
                pass
            else:
                if local_count > countdown_length:
                    local_count = countdown_length
                dancing_to_own_beat = True


def window_is_too_small(w):
    return ((w.getmaxyx()[0] < minimum_height)
            or (w.getmaxyx()[1] < text_width + tap_width))


def unexpected_tap_arrived(lock):
    global sticky_delta, tap_count, last_tap_time
    interval = 0.0001
    with lock:
        tap_count_at_start = tap_count
    time.sleep(interval * 3)
    while True:
        time.sleep(interval)
        with lock:
            if tap_count != tap_count_at_start:
                return True
            elif fmod(time.time() - last_tap_time, sticky_delta) < interval * 5:
                return False


def expected_tap_arrived(lock):
    global sticky_delta, tap_count, last_tap_time
    interval = 0.0001
    tap_arrived = False
    with lock:
        tap_count_at_start = tap_count
    while not tap_arrived:
        time.sleep(interval)
        with lock:
            if time.time() > last_tap_time + sticky_delta * 2:
                return False
            elif tap_count != tap_count_at_start:
                return True


def draw_tap(w, count, dancing_to_own_beat, stream):
    tap = """

         H
        {|}
 ,#############
 #
 #   ..........
[_____]"""
    water = ["\\\\\\", "///"]
    wtr = [" \\ ", " / "]
    droplets = [" ' ", " o ", " O ", " . ", "  .", "  O", "  o", "  '"]
    for i in range(9):
        droplets.append("   ")
    tap_rotate_end = 24
    x = 0
    y = 2

    w.clear()
    w.addstr(y, x, tap.split("\n")[y], red)
    y += 1
    while y < len(tap.split("\n")):
        w.addstr(y, x, tap.split("\n")[y], gray)
        y += 1
    if count < tap_rotate_end:
        w.addstr(1, x + 7, handle(count), red)
    else:
        w.addstr(1, x + 7, handle(tap_rotate_end), red)
    if dancing_to_own_beat:
        if count > 20:
            add_to_stream(stream, water[mod2(count)])
        elif count > 17:
            add_to_stream(stream, wtr[mod2(count)])
        elif count > 2:
            add_to_stream(stream, droplets[randrange(len(droplets))])
        else:
            if randrange(35) == 0:
                add_to_stream(stream, "  .")
            if randrange(80) == 0:
                add_to_stream(stream, ".  ")
            else:
                add_to_stream(stream, "   ")
    else:
        if count > 10:
            add_to_stream(stream, water[mod2(count)])
        elif count > 9:
            add_to_stream(stream, wtr[mod2(count)])
        elif count > 3:
            add_to_stream(stream, droplets[randrange(len(droplets))])
        else:
            add_to_stream(stream, "   ")
    for i in range(len(stream)):
        w.addstr(y + i, x + 2, stream[i], blue)


def add_to_stream(stream, line):
    for i in range(len(stream) - 1, 0, -1):
        stream[i] = stream[i - 1]

    stream[0] = line


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
