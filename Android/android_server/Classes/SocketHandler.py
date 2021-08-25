import json
import socket as s
import selectors
import threading
import types

import logging

logger = logging.getLogger("Main." + __name__)


class SocketHandler:
    socket = None

    sel = selectors.DefaultSelector()
    selector_timeout = 4

    doShutdown = threading.Event()

    connected_sockets = []
    handler_list = []

    def __init__(self, host_addr="localhost", socket_port=5000) -> None:

        self.host_addr = host_addr
        self.port = socket_port

        socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        socket.bind((self.host_addr, self.port))
        socket.listen()
        logger.info(f"Socket listening on: {self.host_addr}:{self.port}")

        socket.setblocking(False)
        self.sel.register(socket, selectors.EVENT_READ, data=None)

        self.listener_thread = threading.Thread(target=self._listener_loop)
        self.listener_thread.start()

    def _accept_and_register(self, sock):
        conn, addr = sock.accept()
        logger.debug(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ  # | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)
        self.connected_sockets.append(conn)

    def _service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:

            # read magic happens here

            recv_data = sock.recv(1)
            recv_data = sock.recv(int.from_bytes(recv_data, "big"))
            logger.debug(f"Received from {data.addr}: {recv_data}")

            if recv_data:
                self._handle_incoming(sock, recv_data)
            else:
                logger.debug(f"closing connection to {data.addr}")
                try:
                    self.sel.unregister(sock)
                    self.connected_sockets.remove(sock)
                except KeyError or ValueError:
                    logger.info(f"There was a failure in unregistering the socket, but should still work fine")

    def _listener_loop(self):
        while not self.doShutdown.is_set():
            events = self.sel.select(timeout=self.selector_timeout)
            if events is None:
                continue
            for key, mask in events:
                if key.data is None:
                    self._accept_and_register(key.fileobj)
                else:
                    try:
                        self._service_connection(key, mask)
                    except Exception as e:
                        if str(e).startswith("[WinError 10054]"):
                            try:
                                self.sel.unregister(key.fileobj)
                                self.connected_sockets.remove(key.fileobj)
                            except ValueError or KeyError as e:
                                logger.debug(f"Error removing socket! {repr(e)}")
                            logger.debug("Socket Closed")
                        else:
                            logger.warning(f"Socket error!  {key.data.addr}:\n{e}")
                            raise e

    def _handle_incoming(self, sock, data: bytes):
        try:
            str_version = data.decode("utf-8")
        except UnicodeDecodeError:
            data = data[1:]
            str_version = data.decode("utf-8")

        str_version = str_version.replace('"true"', 'true').replace('"false"', 'false')

        usable_json = json.loads(str_version)

        for i in self.handler_list:
            i(usable_json)


    def send_all(self, message: str):
        if len(self.connected_sockets) == 0:
            logger.warning("TRY TO SEND MESSAGE TO NOTHING! regards, SocketHandler.send_all()")
        logger.debug("Sending to all sockets: " + message)
        for sock in self.connected_sockets:
            try:
                sock.sendall(message.encode("utf-8") + b"\n")
            except BlockingIOError as e:
                logger.critical(f"Sending IO Error!  {repr(e)}")
            except ConnectionResetError:
                logger.warning("Socket Forcibly close by host")
                try:
                    self.connected_sockets.remove(sock)
                    self.sel.unregister(sock)
                except ValueError  or KeyError:
                    logger.info(f"failed to unregister from something.")

    def register_message_handler(self, function):
        """register function to be called when a message is received from the socket

        Args:
            function ([function(json.JSON)]): [description]
        """
        self.handler_list.append(function)

    def unregister_handler(self, function):
        self.handler_list.remove(self.handler_list.index(function))

    def close(self):
        self.doShutdown.set()
        if len(self.connected_sockets) == 0:
            return
        for i in range(len(self.connected_sockets)):
            self.sel.unregister(self.connected_sockets[i])

        del self.connected_sockets
