__author__ = 'maxvitek'
import sys


def wipe(n):
    for nn in range(n):
        sys.stdout.write("\x1b[A")    # moves up a line
        sys.stdout.write("\r\x1b[K")  # clears the line


def get_visualizer_character(n, level):
    q, r = divmod(n, level)
    if q > 0:
        return '|'
    else:
        return ' '