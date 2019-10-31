import socket, time, os, tempfile, errno, sys
from subprocess import call
from datetime import datetime
from pathlib import Path



BUFFER_SIZE = 8192



def parse_data(data):
    """parses host, port, method, decoded data from request and returns them"""

    print("[parse data]:\n{}\n".format(str(data)))

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

    # host_line = data.split(b'\n')[1]
    # host_line_arr = host_line.split(b':')
    # print("host_line_arr: " + str(host_line_arr))
    # if len(host_line_arr) == 2:
    #     host = host_line_arr[0]
    #     port = host_line_arr[1]
    # elif len(host_line_arr) == 1:
    #     host = host_line_arr[0]
    #     port = 80
    # else:
    #     print("Can't handle the request... Exiting...")
    #     sys.exit(2)

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


def set_path_original(data, host, port):
    data_arr = data.split(' ')
    path_orig = "http://" + host.decode('utf-8') + ":" + str(port) + data_arr[1]
    data_arr[1] = path_orig

    return str(' '.join(data_arr))


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
        print("proxy server\n" + str(self.data))
        print("[Host]: {}\n[Port]: {}\n".format(self.host, self.port))
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
                    if self.conn:
                        self.conn.send(res)
                    result = result + res.decode('utf-8')
                else:
                    break
            self.response = result

            s.close()
            if self.conn:
                self.conn.close()

            return

        except socket.error:
            print("[ERROR]\n{}".format(socket.error))
            s.close()
            if self.conn:
                self.conn.close()

            return

            
    def process_request(self):
        os.system("clear")
        print("[REQUEST]\n{}\n".format(self.data))
        print("1) Forward request")
        print("2) Modify request")
        print("3) Save request")
        while(True):
            r = int(input("> "))
            if r in range(1, 4):
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
        
        elif r == 3:
            # Save request
            now = datetime.now()
            default_name = "Request-" + now.strftime("%Y-%m-%d") + "-at-" + now.strftime("%H-%M-%S")
            name = input("File name [default: " + default_name + "] > ")
            if name == '':
                name = default_name
            filename = str(Path.home()) + "/.appdata/proxpy/" + name + ".req"

            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc: 
                    # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            data_with_orig_path = set_path_original(self.data, self.host, self.port)
            with open(filename, "w") as f:
                f.write(data_with_orig_path)

            print("Saved request in: " + filename)
            time.sleep(2)

            self.process_request()
