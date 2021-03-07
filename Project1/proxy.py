import os, sys, thread, socket, time
import Tkinter as tk
from TKinter import *

# CONSTRAINTS
BACKLOG = 200 # Maximum pending connections
MAX_DATA_RECV = 4096 # Max number of bytes received 
DEBUG = True
blocked = {}
cache = {}
timings = {}

# Tkinter function used to dynamically block URLs and display cache/blocked URLs
# Creates buttons for managment console
def tkinter():
    console = tk.Tk()
    block = Entry(console)
    block.grid(row=0, column=0)
    unblock = Entry(console)
    unblock.grid(row=1, column=0)

    # Funciton to dynamically block URLs
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

    # Function to dynamically unblock URLs
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

    # Function to print the currently blocked URLs
    def print_blocked():
        print(blocked)

    print_blocked = Button(console,
                           text="Print Blocked URLs",
                           command=print_blocked)
    print_blocked.grid(row=3, column=0)

    # Function to print the cache
    def print_cached():
        for key, value in cache.iteritems():
            print key

    print_cached = Button(console, text="Print Cache", command=print_cached)
    print_cached.grid(row=3, column=1)

    mainloop()

def main():
    # Run new thread
    thread.start_new_thread(tkinter,())
    listening_port = int(raw_input("Enter Listening Port Number: "))

    try:
        #initiate websocket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('', listening_port))				
		s.listen(BACKLOG)						
		print("Sockets binded successfully...")
		print("Server started successfully at port: [ %d ]\n" % (listening_port))
    except Exception, e:
		print("Unable to initalize socket...")
		sys.exit()

    # While connection initiated
    while True:
		try:
			# Accept connection from client browser
			conn, client_addr = s.accept()		
			data = conn.recv(MAX_DATA_RECV)		
			# Start a new thread
			thread.start_new_thread(proxy_thread, (conn, data, client_addr)) 
		except KeyboardInterrupt:
			s.close()
			print("Proxy server shutting down...")
			sys.exit(1)
	s.close()

def proxy_thread(conn, data, client_addr):
    