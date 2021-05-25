import socket as s
import selectors
import time
import threading
import types

from utils import threaded

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%H:%M:%S')
#datefmt='%m/%d/%Y %H:%M:%S'
logger = logging.getLogger("SocketHandeler")

class SocketHandler:

    socket = None

    sel = selectors.DefaultSelector()
    selector_timeout = 4

    doShutdown = threading.Event()

    connected_sockets = []

    host_addr = "localhost"
    port = 5000

    def __init__(self) -> None:
        socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        socket.bind((self.host_addr, self.port))
        socket.listen()
        logger.debug(f"Socket listening on: {self.host_addr}:{self.port}")

        socket.setblocking(False)
        self.sel.register(socket, selectors.EVENT_READ, data=None)

        self.listener_thread = threading.Thread(target=self._listener_loop)
        self.listener_thread.start()


    def _listener_loop(self):
        while not self.doShutdown.is_set():
            events = self.sel.select(timeout=self.selector_timeout)
            if events == None:
                continue
            for key, mask in events:
                if key.data is None:
                    self._accept_and_register(key.fileobj)
                else:
                    self._service_connection(key, mask)

    def _accept_and_register(self, sock):
        conn, addr = sock.accept()
        logger.debug(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ #only listen for incoming events
        self.sel.register(conn, events, data=data)
        self.connected_sockets.append(conn)
    
    def _service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:

            # read the incoming length
            recv_data = sock.recv(1)
            #print(recv_data)
            #print(int.from_bytes(recv_data[:1], "big"))
            recv_data = sock.recv(int.from_bytes(recv_data[:1], "big"))
            print(repr(recv_data))
            #current code is for an echo server
            if recv_data:
                data.outb += recv_data
            else:
                logger.debug(f"closing connection to {data.addr}")
                self.sel.unregister(sock)
                sock.close()

        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print(f"echoing {repr(data.outb)} to {data.addr}")
                sent = sock.send(data.outb)
                data.outb = data.outb[sent:]

    def send_all(self, message: bytes):
        for sock in self.connected_sockets:
            sock.sendall(message+b"\n")

    def close(self):
        self.doShutdown.set()

@threaded
def sneaky_sending_to_sockets(socket:SocketHandler):
    message = b"tehe, this is a psuedo-random message for you!"
    time.sleep(15)
    socket.send_all(message)


socket = SocketHandler()
sneaky_sending_to_sockets(socket)
input()
socket.close()