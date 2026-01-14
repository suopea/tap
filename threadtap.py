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

    global tap_count, tempo, last_tap_time
    tap_count = 1
    last_tap_time = time.time()
    tempo = 1000
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
            tempo = current_delta(times)
            last_tap_time = time.time()
    with lock:
        tap_count = 0
    draw_thread.join(3)


def current_delta(times):
    time_count = len([i for i in times if i])
    ideal_smoothness = 3
    if time_count > ideal_smoothness:
        return delta(times, ideal_smoothness)
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


def draw(w, lock):
    global tap_count, tempo
    local_count = 0
    countdown_length = 20
    dancing_to_own_beat = False
    while tap_count < 3:
        pass
    while True:
        with lock:
            if tap_count == 0:
                break
        draw_tap(w, local_count)
        if dancing_to_own_beat:
            w.addstr(0, 0, f"own     {local_count}")
        else:
            w.addstr(0, 0, f"not own {local_count}")
        w.noutrefresh()
        curses.doupdate()
        if dancing_to_own_beat:
            if local_count > 0:
                local_count += -1
            if unexpected_tap_arrived(lock):
                dancing_to_own_beat = False
        else:
            if expected_tap_arrived(lock):
                local_count += 1
            else:
                if local_count > countdown_length:
                    local_count = countdown_length
                dancing_to_own_beat = True


def unexpected_tap_arrived(lock):
    global tempo, tap_count, last_tap_time
    interval = 0.0001
    with lock:
        tap_count_at_start = tap_count
    time.sleep(interval * 3)
    while True:
        time.sleep(interval)
        with lock:
            if tap_count != tap_count_at_start:
                return True
            elif fmod(time.time() - last_tap_time, tempo) < interval * 5:
                return False


def expected_tap_arrived(lock):
    global tempo, tap_count, last_tap_time
    interval = 0.0001
    tap_arrived = False
    with lock:
        tap_count_at_start = tap_count
    while not tap_arrived:
        time.sleep(interval)
        with lock:
            if time.time() > last_tap_time + tempo * 2:
                return False
            elif tap_count != tap_count_at_start:
                return True


def draw_tap(w, count):
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
    for i in range(count - stream_start):
        w.addstr(y, x + 2, water[mod2(count + mod2(y))], blue)
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
