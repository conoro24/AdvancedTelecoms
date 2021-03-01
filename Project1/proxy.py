import os, sys, thread, socket, time
import Tkinter as tk
from TKinter import *

# CONSTRAINTS
BACKLOG = 200
MAX_DATA_RECV = 4096
DEBUG = True
blocked = {}
cache = {}
timings = {}


def tkinter():
    console = tk.Tk()
    block = Entry(console)
    block.grid(row=0, column=0)
    unblock = Entry(console)
    unblock.grid(row=1, column=0)

    def block_url():
        val = block.get()
        temp = blocked.get(val)
        if temp is None:
            blocked[val] = 1
            print("Successfully Blocked: " + val)
        else:
            print("This website is already blocked...")

    block_button = Button(console, text="Block URL", command=block_url)
    block_button.grid(row=0, column=1)

    def unblock_url():
        val = unblock.get()
        temp = blocked.get(val)
        if temp is None:
            print("The URL is not blocked: " + val)
        else:
            blocked.pop(val)
            print("This website is unblocked: " + val)

    unblock_button = Button(console, text="Unblock URL", command=unblock_url)
    unblock_button.grid(row=1, column=1)

    def print_blocked():
        print(blocked)

    print_blocked = Button(console,
                           text="Print Blocked URLs",
                           command=print_blocked)
    print_blocked.grid(row=3, column=0)

    def print_cached():
        for key, value in cache.iteritems():
            print key

    print_cached = Button(console, text="Print Cache", command=print_cached)
    print_cached.grid(row=3, column=1)
