#! /usr/bin/env python3
import socket, sys, time
import _thread
from pyfiglet import Figlet


LISTENING_PORT = 7001
MAX_CONN = 5
BUFFER_SIZE = 8192



def proxy_server(host, port, conn, data):
    # print("[*] Proxy server")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(data)

        timeout = 2
        timeout_start = time.time()
        result = ""
        while(time.time() < timeout_start + timeout):
            res = s.recv(BUFFER_SIZE)

            if (len(res) > 0):
                conn.send(res)
                result = result + res.decode('utf-8')
            else:
                break

        print("[RESPONSE]\n{}\n".format(result))

        s.close()
        conn.close()

        return
    except socket.error:
        s.close()
        conn.close()
        return



def handle_conn(conn, data):
    """read destination host and port from request to forward request to remote host"""

    first_line = data.split(b'\n')[0]

    url = first_line.split(b' ')[1]

    http_pos = url.find(b"://")
    if http_pos == -1:
        full_addr = url
    else:
        full_addr = url[(http_pos+3):]

    port_pos = full_addr.find(b":")

    host_pos = full_addr.find(b"/")
    if host_pos == -1:
        host_pos = len(full_addr)
    
    if port_pos == -1 or host_pos < port_pos:
        port = 80
        host = full_addr[:host_pos]
    else:
        port = int((full_addr[(port_pos+1):])[:host_pos-port_pos-1])
        host = full_addr[:port_pos]

    # Remove host from requested resource path
    data_str = data.decode('utf-8')
    data_new = data_str.split(' ')
    path_orig = data_new[1]
    path_orig_arr = path_orig.split('/')
    if len(path_orig_arr) > 3:
        path_new = '/' + '/'.join(path_orig_arr[3:])
    else:
        path_new = '/'

    data_new[1] = path_new

    data_str_new = str(' '.join(data_new))
    data = data_str_new.encode('utf-8')

    print("[REQUEST]\n{}\n".format(data_str_new))

    proxy_server(host, port, conn, data)

    return



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

    while(True):
        try:
            conn, addr = s.accept()
            data = conn.recv(BUFFER_SIZE)
            # _thread.start_new_thread(handle_conn, (conn, data))
            handle_conn(conn, data)
        except KeyboardInterrupt:
            s.close()
            print("\n[*] Shutting down...")
            sys.exit(1)

start()