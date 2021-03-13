import os
import sys
import threading
from threading import *
import socket
import time
import tkinter as tk
from tkinter import *

TK_SILENCE_DEPRECATION = 1

# CONSTRAINTS
BACKLOG = 200  # Maximum pending connections
MAX_DATA = 4096  # Max number of bytes that can be received
DEBUG = True
blocked = {}
cache = {}
listening_port = 8001


# Tkinter function used to dynamically block URLs and display cache/blocked URLs
# Creates buttons for managment console
def tkinter():

    console = tk.Tk()
    block = Entry(console)
    block.grid(row=0, column=0)
    unblock = Entry(console)
    unblock.grid(row=1, column=0)

    def threads():
        t1 = Thread(target=block_url)
        t1.start()
        t2 = Thread(target=unblock_url)
        t2.start()
        t3 = Thread(target=print_blocked)
        t3.start()
        t4 = Thread(target=print_cached)
        t4.start()


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
            print(key)

    print_cached = Button(console, text="Print Cache", command=print_cached)
    print_cached.grid(row=3, column=1)

    console.mainloop()


class Proxy():
    # Call tkninter function to run new thread
    # tkinter()
    def __init__(self):

        try:
            # initiate websocket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind(('localhost', listening_port))
            self.s.listen(BACKLOG)
            print("Sockets binded successfully...")
            print("Server started successfully at port: [ %d ]\n" %
                  (listening_port))
        except Exception:
            print("Unable to initalize socket...")
            sys.exit()

        # While connection active
        while True:

            # Accept connection from client browser
            (conn, client_addr) = self.s.accept()

            # Start a new thread
            y = threading.Thread(target=proxy_thread,
                                 args=(conn, client_addr))
            y.start()

        # close connection
        s.close()


def proxy_thread(conn, client_addr):

    print("Starting new thread...")

    try:
        # checking the request
        request = conn.recv(MAX_DATA)
        first_line = request.split("\n")[0]
        url = first_line.split(" ")[1]
        method = first_line.split(" ")[0]
        print("Connecting to " + url)
        print("Method: " + method)

        # find http position
        http_pos = url.find("://")
        if (http_pos == -1):
            temp = url
        else:
            temp = url[(http_pos + 3):]

        # find port position
        port_pos = temp.find(":")

        # find termination of url
        webserver_pos = temp.find("/")
        if (webserver_pos == -1):
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        # if no port specified... default port
        if (port_pos == -1 or webserver_pos < port_pos):
            port = 80
            webserver = temp[:webserver_pos]
        # specified port...
        else:
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]

        # check if cached
        t0 = time.time()
        x = cache.get(webserver)

        if x is not None:
            # If cached, send response..
            print("Found in Cache!")
            print("Sending response to user...")
            conn.sendall(x)
            t1 = time.time()
            print("Request took: " + str(t1 - t0) + "s with cache.")
        else:
            # If we don't, call function to processs request
            proxy_server(webserver, port, conn, client_addr, request, method)

    except Exception:
        pass


def proxy_server(webserver, port, conn, client_addr, request, method):
    # initiate websocket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(20)
    # check if URL is blocked
    for key, value in blocked.iteritems():
        if key in webserver and value == 1:
            print("That url is blocked!")
            conn.close()
            return

    # If method is CONNECT, we know it is HTTPS
    if method == "CONNECT":
        try:
            s.connect((webserver, port))
            reply = "HTTP/1.0 200 Connection established\r\n"
            reply += "Proxy-agent: Pyx\r\n"
            reply += "\r\n"
            print("Sending connection to server..")
            conn.sendall(reply.encode())  # conn -> s
        except socket.error:
            print(socket.error)
            return
        conn.setblocking(0)
        s.setblocking(0)
        print("Websocket connection is active...")

        while True:
            # receive request from client
            request = conn.recv(MAX_DATA)
            # send request to server
            s.sendall(request)
            # receive reply from server
            reply = s.recv(MAX_DATA)
            # send reply to client
            conn.sendall(reply)
        print("Sending response to client...")

    # else we know its a HTTP request
    else:
        t0 = time.time()
        s.connect((webserver, port))
        string_for_cache = bytearray("", 'utf-8')
        print("Sending request to server...")
        s.sendall(request)
        s.settimeout(20)
        while True:
            # receive response from server
            reply = s.recv(MAX_DATA)
            if (len(reply) > 0):
                # send response to client
                conn.send(reply)
                string_for_cache.extend(reply)
            else:
                break
        print("Sending response to client...")
        t1 = time.time()
        print("Request took: " + str(t1 - t0) + "s")
        cache[webserver] = string_for_cache
        print("Added to cache: " + webserver)
        # close connections
        s.close()
        conn.close()


if __name__ == '__main__':
    Proxy()
