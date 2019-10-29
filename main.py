#! /usr/bin/env python3
import socket, sys, time, queue
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
        conn.print_data()
        conn.proxy_server()
        time.sleep(3)
    
def start():
    """start listening for incoming connections and spawn threads for them"""

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
            # _thread.start_new_thread(handle_conn, (conn, data))
            # handle_conn(conn, data)
            connections.put((conn, data))
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Shutting down...")
            sys.exit(1)

start()
