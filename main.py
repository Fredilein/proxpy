#! /usr/bin/env python3
import socket, sys, time, queue, os
import _thread
from pyfiglet import Figlet
from connection import Connection
from pathlib import Path



BUFFER_SIZE = 8192
LISTENING_PORT = 7001
MAX_CONN = 5



connections = queue.Queue(maxsize=100)


def handle_connections():
    """thread which works through the connections queue"""

    while(True):
        conn_tuple = connections.get()
        conn = Connection(conn_tuple)
        if conn.method == "CONNECT":
            continue
        conn.process_request()
        os.system("clear")
        print("Waiting for request...")

def load_connection():
    path = str(Path.home()) + "/.appdata/proxpy/"
    if not os.path.isdir(path):
        print("No requests found")
        return

    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    if len(files) < 1:
        print("No saved requests found")
        return

    for i, f in enumerate(files, start=1):
        print("{}) {}".format(i, f))

    while(True):
        r = int(input("> "))
        if r in range(1, len(files)+1):
            break
        else:
            print("Get your shit together")
    
    with open(path+files[r-1], "r") as f:
        data = f.read().encode('utf-8')
    
    conn = Connection(("", data))
    conn.process_request()
    return

    

def start():
    """thread which listens for incoming connections and puts them in the connections queue"""

    os.system("clear")
    f = Figlet(font='slant')
    print(f.renderText('proxpy'))

    print("1) Intercept")
    print("2) Load request")
    while(True):
        r = int(input("> "))
        if r in range(1, 3):
            break
        else:
            print("Get your shit together")

    if r == 1:

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', LISTENING_PORT))
            s.listen(MAX_CONN)
            print("[*] Initialized Sockets")
            print("[*] Server started on port {}\n".format(LISTENING_PORT))
        except Exception as e:
            print("[!] Unable to initialize socket")
            print("[!] Error: {}".format(e))
            sys.exit(2)

        _thread.start_new_thread(handle_connections, ())

        while(True):
            try:
                conn, _ = s.accept()
                data = conn.recv(BUFFER_SIZE)
                connections.put((conn, data))
            except KeyboardInterrupt:
                print("\n[*] Shutting down...")
                s.close()
                os.system("clear")
                sys.exit(1)

    elif r == 2:
        
        load_connection()


start()
