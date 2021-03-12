import os, sys, thread, socket, time
import Tkinter as tk
from TKinter import *

# CONSTRAINTS
BACKLOG = 200 # Maximum pending connections
MAX_DATA = 4096 # Max number of bytes that can be received 
DEBUG = True
blocked = {}
cache = {}

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

    # While connection active
    while True:
		try:
			# Accept connection from client browser
			conn, client_addr = s.accept()		
			data = conn.recv(MAX_DATA)		
			# Start a new thread
			thread.start_new_thread(proxy_thread, (conn, data, client_addr)) 
		except KeyboardInterrupt:
			s.close()
			print("Proxy server shutting down...")
			sys.exit(1)
    #close connection
	#s.close()

def proxy_thread(conn, data, client_addr):

    print("Starting new thread...")

    try:
        #checking the request
        first_line = data.split("\n")[0]
        url = first_line.split(" ")[1]
        method = first_line.split(" ")[0]
        print("Connecting to " + url)
        print("Method: " + method)

        #find http position
        http_pos = url.find("://")
        if (http_pos == -1):
            temp = url
        else:
            temp = url[(http_pos + 3):]
        
        #find port position
        port_pos = temp.find(":")

        #find termination of url
        webserver_pos = temp.find("/") 	
        if (webserver_pos == -1):
		    webserver_pos = len(temp)

        webserver == ""
        port == -1
        #if no port specified... default port
        if (port_pos == -1 or webserver_pos < port_pos):	
			port = 80
			webserver = temp[:webserver_pos]
        #specified port...
        else:
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        #check if cached
        t0 = time.time()
        x = cache.get(webserver)
        
        if x is not None:
			#If cached, send response..
			print("Found in Cache!")
			print("Sending response to user...")
			conn.sendall(x)
			t1 = time.time()
			print("Request took: " + str(t1-t0) + "s with cache.")
        else:
			# If we don't, call function to processs request
			proxy_server(webserver, port, conn, client_addr, data, method)
            
    except Exception, e:
		pass
        


def proxy_server(webserver, port, conn, client_addr, data, method):
    #initiate websocket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #check if URL is blocked
    for key, value in blocked.iteritems():
		if key in webserver and value is 1:
			print("That url is blocked!")
			conn.close()
			return

    #If method is CONNECT, we know it is HTTPS
    if method == "CONNECT":
        try:
            s.connect((webserver, port))
            reply = "HTTP/1.0 200 Connection established\r\n"
            reply += "Proxy-agent: Pyx\r\n"
            reply += "\r\n"
            print("Sending connection to server..")
            conn.sendall(reply.encode())
        except socket.error:
            print(socket.error)
            return
        conn.setblocking(0)
        s.setblocking(0)
        print("Websocket connection is active...")

        while True:
			try:
				#receive request from client
				request = conn.recv(MAX_DATA)
				#send request to server
				s.sendall(request)
			except socket.error as err:
				pass
			try:
				#receive reply from server
				reply = s.recv(MAX_DATA)
				#send reply to client
				conn.sendall(reply)
			except socket.error as err:
				pass
        print("Sending response to client...")

    # else we know its a HTTP request
    else:
        t0 = time.time()
        s.connect((webserver, port))
        string_for_cache = bytearray("", 'utf-8')
        print("Sending request to server...")
        s.send(data)
        s.settimeout(2)
        try:
			while True:
				#receive response from server
				reply = s.recv(MAX_DATA)
				if (len(reply) > 0):
					#send response to client
					conn.send(reply)
                        string_for_cache.extend(reply)
                else:
                    break
		except socket.error:
			pass
		print("Sending response to client...")
		t1 = time.time()
		print("Request took: " + str(t1-t0) + "s") 
		cache[webserver] = string_for_cache
		print("Added to cache: " + webserver)
		#close Server and Client socket
		s.close()		
		conn.close()

if __name__ == '__main__':
	main()

