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
