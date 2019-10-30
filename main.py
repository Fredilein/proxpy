#! /usr/bin/env python3
import socket, sys, time, queue, os
import _thread
from pyfiglet import Figlet
from connection import Connection



BUFFER_SIZE = 8192
LISTENING_PORT = 7001
MAX_CONN = 5



connections = queue.Queue(maxsize=100)


def handle_connections():
    while(True):
        conn_tuple = connections.get()
        conn = Connection(conn_tuple)
        if conn.method == "CONNECT":
            continue
        conn.process_request()
        os.system("clear")
        print("Waiting for request...")
    

def start():
    """listen for incoming connections and put them in the connections queue"""

    os.system("clear")
    f = Figlet(font='slant')
    print(f.renderText('proxpy'))

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


start()
