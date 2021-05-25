
import json
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
    handler_list = []

    host_addr = "localhost"
    port = 5000

    def __init__(self, host_addr, socket_port) -> None:

        self.host_addr = host_addr
        self.port = socket_port

        socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        socket.bind((self.host_addr, self.port))
        socket.listen()
        logger.debug(f"Socket listening on: {self.host_addr}:{self.port}")

        socket.setblocking(False)
        self.sel.register(socket, selectors.EVENT_READ, data=None)

        self.listener_thread = threading.Thread(target=self._listener_loop)
        self.listener_thread.start()   

    def _accept_and_register(self, sock):
        conn, addr = sock.accept()
        logger.debug(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ #| selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)
        self.connected_sockets.append(conn)
    
    def _service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:

            #read magic happens here

            recv_data = sock.recv(1)
            recv_data = sock.recv(int.from_bytes(recv_data, "big"))
            logger.debug(f"Recieve from {data.addr}: {recv_data}")
            logger.critical(repr(sock))
            
            if recv_data:
                self._handle_incoming(sock, recv_data)
            else:
                logger.debug(f"closing connection to {data.addr}")
                self._close_socket(sock)

    def _listener_loop(self):
        while not self.doShutdown.is_set():
            events = self.sel.select(timeout=self.selector_timeout)
            if events == None:
                continue
            for key, mask in events:
                if key.data is None:
                    self._accept_and_register(key.fileobj)
                else:
                    try:
                        self._service_connection(key, mask)
                    except Exception as e:
                        if ((str)(e).startswith("[WinError 10054]")):
                            self._close_socket(key.fileobj)
                            logger.debug("Socket Closed")
                        else:
                            logger.warning(f"Socket error!  {key.data.addr}:\n{e}")

    def _handle_incoming(self, sock, data:bytes):        
        try:
            str_version = data.decode("utf-8")
        except UnicodeDecodeError:
            data = data[1:]
            str_version = data.decode("utf-8")

        logger.debug(json.loads(str_version))  

    def _prune_sockets(self):
        index = 0
        while(index < len(self.connected_sockets)):
            if (self.connected_sockets[index].fileno() == -1):
                del self.connected_sockets[index]
                index = 0

    def _close_socket(self, sock):
        try:
            self.connected_sockets.remove(self._find_same_addr_index(sock))
        except ValueError:
            pass
        except Exception as e:
                logger.warning(f"Error removing socket from list: {repr(e)}")
    
        try:
            self.sel.unregister(sock)
            sock.close()
        except Exception as e:
                logger.warning(f"Error unregistering or closing socket: {repr(e)}")

        self._prune_sockets()


    def _find_same_addr_index(self, sock):
        for i in range(len(self.connected_sockets)-1):
            if self.connected_sockets[i].raddr == sock.raddr:
                return i

    def send_all(self, message: bytes):
        if (len(self.connected_sockets) == 0):
            logger.critical("TRY TO SEND MESSAGE TO NOTHING! regards, SocketHandler.send_all()")
        for sock in self.connected_sockets:
            try:
                sock.sendall(message+b"\n")
            except BlockingIOError as e:
                logger.critical(f"Sending IO Error!  {repr(e)}")
            except ConnectionResetError as e:
                logger.warning("Socket Forcibly close by host")
                self._close_socket(sock)

    def register_json_handler(self, function):
        self.handler_list.append(function)

    def unregister_handler(self, function):
        self.handler_list.remove(self.handler_list.index(function))

    def close(self):
        self.doShutdown.set()
        if (len(self.connected_sockets) == 0):
            return
        for i in range(len(self.connected_sockets)):
            self._close_socket(self.connected_sockets[i])
            

@threaded
def sneaky_sending_to_sockets(socket:SocketHandler):
    message = b"tehe, this is a psuedo-random message for you!"
    time.sleep(15)
    if (not socket.doShutdown.is_set()):
        socket.send_all(message)



if (__name__ == "__main__"):
    socket = SocketHandler("localhost", 5000)
    #sneaky_sending_to_sockets(socket)
    input()
    socket.close()