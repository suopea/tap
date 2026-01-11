import curses
import time


def main(w):
    w.clear()
    key = 'key'
    time1 = 0
    time2 = 0
    time3 = 0
    time4 = 0
    w.addstr(0, 0, "tap any key (or q to quit)")
    while key not in "q":
        key = w.getkey()
        curses.flash()
        w.clear()
        time2, time3, time4 = time1, time2, time3
        time1 = time.time()
        w.addstr(5, 0, f"{time1} {time2} {time3} {time4}")
        if time4 == 0:
            w.addstr(0, 0, "keep tapping")
        else:
            # delta = (time1 - time4) / 3
            delta = time1 - time2
            if delta:
                bpm = (1 / delta) * 60
            else:
                bpm = 420
            w.addstr(0, 0, f"BPM: {bpm:.2f} delta {delta}")
    print(bpm)


curses.wrapper(main)
