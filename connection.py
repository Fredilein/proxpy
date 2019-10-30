import socket, time, os, tempfile
from subprocess import call



BUFFER_SIZE = 8192



def parse_data(data):
    """parses host, port, method, decoded data from request and returns them"""

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
    data_arr = data_str.split(' ')
    path_orig = data_arr[1]
    path_orig_arr = path_orig.split('/')
    if len(path_orig_arr) > 3:
        path_new = '/' + '/'.join(path_orig_arr[3:])
    else:
        path_new = '/'
    data_arr[1] = path_new

    data_new = str(' '.join(data_arr))
    data = data_new.encode('utf-8')

    method = data_arr[0]

    return host, port, data_new, method


class Connection:


    def __init__(self, c):
        host, port, data, method = parse_data(c[1])
        self.conn = c[0]
        self.host = host
        self.port = port
        self.data = data
        self.method = method
        self.response = ""


    def proxy_server(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            s.send(self.data.encode('utf-8'))

            timeout = 2
            timeout_start = time.time()
            result = ""
            while(time.time() < timeout_start + timeout):
                res = s.recv(BUFFER_SIZE)
                if (len(res) > 0):
                    self.conn.send(res)
                    result = result + res.decode('utf-8')
                else:
                    break
            self.response = result

            s.close()
            self.conn.close()

            return

        except socket.error:
            s.close()
            self.conn.close()

            return

            
    def process_request(self):
        os.system("clear")
        print("[REQUEST]\n{}\n".format(self.data))
        print("1) Forward request")
        print("2) Modify request")
        while(True):
            r = int(input("> "))
            if r in [1, 2]:
                break
            else:
                print("Get your shit together")

        if r == 1:
            # Forward request
            self.proxy_server()
            os.system("clear")
            print("[REQUEST]\n{}\n".format(self.data))
            print("[RESPONSE]\n{}\n".format(self.response))
            input("> Continue ")

        elif r == 2:
            # Modify request
            editor = os.environ.get('EDITOR', 'vim')
            with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
                tf.write(self.data.encode('utf-8'))
                tf.flush()
                call([editor, tf.name])
                tf.seek(0)
                self.data = tf.read().decode('utf-8')

            self.process_request()
