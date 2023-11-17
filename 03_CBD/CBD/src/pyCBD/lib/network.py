"""
This file contains the CBD building blocks that can be used in networking communications.

Warning:
    This code is currently in beta and not yet ready to be used in applications. Many parts
    may be subject to change.

Note:
    Future releases may also include non-TCP sockets.
"""
from pyCBD.Core import BaseBlock
import socket

class TCPClientSocket:
    """
    Client socket for a TCP connection. This class provides a simple interface
    for the required features.

    Args:
        host (str):         The hostname of the server to connect to.
        port (str or int):  The port of the server connection.

    See Also:
        - :class:`TCPServerSocket`
        - :class:`ClientSender`
        - :class:`ClientReceiver`
        - `:code:`socket` module documentation <https://docs.python.org/3/library/socket.html>`_
    """
    def __init__(self, host, port):
        self.address = host, port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.address)

    def __del__(self):
        self.socket.close()

    def setblocking(self, val):
        """
        Sets whether or not the socket must be blocking.

        Args:
            val (bool): Blocking or not.
        """
        self.socket.setblocking(val)

    def send(self, data, enc="utf-8"):
        """
        Sends data in a certain encoding over the socket connection.

        Args:
            data (str): Message to send.
            enc (str):  The encoding to use. When :code:`None`, no encoding will be
                        done. This should be used if :attr:`data` is a :code:`bytes`
                        object instead. Defaults to :code:`"utf-8"`.
        """
        if enc is not None:
            data = data.encode(enc)
        self.socket.send(data)

    def recv(self, buffer_size, enc="utf-8"):
        """
        Receives data in a certain encoding from the socket connection.

        Args:
            buffer_size (int):  The maximum amount of data to receive.
            enc (str):          The encoding to use. When :code:`None`, no decoding will be
                                done. Defaults to :code:`"utf-8"`.
        """
        val = self.socket.recv(buffer_size)
        if enc is not None:
            val = val.decode(enc)
        return val


class TCPServerSocket:
    """
    Server socket for a TCP connection. This class provides a simple interface
    for the required features.

    Args:
        host (str):         The hostname of the server to connect to.
        port (str or int):  The port of the server connection.
        connections (int):  The amount of clients to wait for. Defaults to 1.

    See Also:
        - :class:`TCPServerSocket`
        - :class:`ClientSender`
        - :class:`ClientReceiver`
        - `:code:`socket` module documentation <https://docs.python.org/3/library/socket.html>`_
    """
    def __init__(self, host, port, connections=1):
        self.address = host, port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)

        self.socket.listen(connections)
        self.clients = []
        clen = len(str(connections))
        for i in range(connections):
            self.clients.append(self.socket.accept())
            print("[{}/{}] Connected to".format((" " * clen + str(i))[-clen:], connections), self.clients[-1][1])

    def __del__(self):
        self.socket.close()

    def setblocking(self, val):
        """
        Sets whether or not the socket must be blocking.

        Args:
            val (bool): Blocking or not.
        """
        self.socket.setblocking(val)

    def send(self, data, enc="utf-8"):
        """
        Sends data in a certain encoding over the socket connection.

        Args:
            data (str): Message to send.
            enc (str):  The encoding to use. When :code:`None`, no encoding will be
                        done. This should be used if :attr:`data` is a :code:`bytes`
                        object instead. Defaults to :code:`"utf-8"`.
        """
        if enc is not None:
            data = data.encode(enc)
        self.socket.send(data)

    def recv(self, client_id, buffer_size, enc="utf-8"):
        """
        Receives data in a certain encoding from the socket connection.

        Args:
            client_id (int):    Client id to receive data from.
            buffer_size (int):  The maximum amount of data to receive.
            enc (str):          The encoding to use. When :code:`None`, no decoding will be
                                done. Defaults to :code:`"utf-8"`.
        """
        msg = self.clients[client_id][0].recv(buffer_size)
        if enc is not None:
            msg = msg.decode(enc)
        return msg


class ClientSender(BaseBlock):
    """
    Sends data over a socket connection.

    Args:
        block_name (str):           Name of the block.
        socket (TCPClientSocket):   Socket to send the data over.
        format (str):               Format of the data to send. Use :code:`{}` to refer
                                    to the obtained data. Defaults to :code:`"{}"` (simple
                                    string conversion).
    """
    def __init__(self, block_name, socket, format="{}"):
        BaseBlock.__init__(self, block_name, ["IN1"], [])
        self.format = format
        self.socket = socket

    def compute(self, curIteration):
        value = self.getInputSignal(curIteration).value
        self.socket.send(self.format.format(value))


class ClientReceiver(BaseBlock):
    """
    Receives data over a socket connection. If no data can be obtained, the previous
    value will be outputted.

    Note:
        The socket used will automatically be converted to a non-blocking socket.

    Args:
        block_name (str):           Name of the block.
        socket (TCPClientSocket):   Socket to send the data over.
        buffer_size (int):          The maximum amount of data to receive.
        convert:                    Conversion function that's executed on all received
                                    data. Defaults to :code:`lambda x:x` (no conversion).
        initial (Any):              The initial value to use.
    """
    def __init__(self, block_name, socket, buffer_size, convert=lambda x: x, initial=""):
        BaseBlock.__init__(self, block_name, [], ["OUT1"])
        self.buffer_size = buffer_size
        self.convert = convert
        self.value = initial

        self.socket = socket
        self.socket.setblocking(False)

    def compute(self, curIteration):
        try:
            self.value = self.convert(self.socket.recv(self.buffer_size))
        except socket.error as e: pass
        self.appendToSignal(self.value)


class ServerSender(BaseBlock):
    """
    Sends data over a socket connection, as a server. The data will be broadcast
    to all clients that are connected to this server.

    Args:
        block_name (str):           Name of the block.
        socket (TCPServerSocket):   Socket to send the data over.
        format (str):               Format of the data to send. Use :code:`{}` to refer
                                    to the obtained data. Defaults to :code:`"{}"` (simple
                                    string conversion).
    """
    def __init__(self, block_name, socket, format="{}"):
        BaseBlock.__init__(self, block_name, ["IN1"], [])
        self.format = format
        self.socket = socket

    def compute(self, curIteration):
        value = self.getInputSignal(curIteration).value
        value = self.format.format(value)
        for conn, _ in self.socket.clients:
            conn.send(value)


class ServerReceiver(BaseBlock):
    """
    Receives data over a socket connection. If no data can be obtained, the previous
    value will be outputted. Messages are assumed to be newline-separated.

    Note:
        The socket used will automatically be converted to a non-blocking socket.

    Args:
        block_name (str):           Name of the block.
        socket (TCPServerSocket):   Socket to send the data over.
        buffer_size (int):          The maximum amount of data to receive.
        convert:                    Conversion function that's executed on all received
                                    data. Defaults to :code:`lambda x:x` (no conversion).
        initial (list):             The initial values to use (one for each connection).
                                    Defaults to :code:`None` (i.e. uses a list of empty strings).
    """
    def __init__(self, block_name, socket, buffer_size, convert=lambda x: x, initial=None):
        BaseBlock.__init__(self, block_name, [], ["OUT%d" % (x + 1) for x in range(len(socket.clients))])
        self.buffer_size = buffer_size
        self.convert = convert
        self.values = [""] * len(socket.clients) if initial is None else initial
        self.last = ""

        self.socket = socket
        self.socket.setblocking(False)

    def compute(self, curIteration):
        # TODO: clean up; add message separator...
        for i in range(len(self.socket.clients)):
            try:
                self.last += self.socket.recv(i, self.buffer_size)
                sp = self.last.split("\n")
                if len(sp) >= 2:
                    self.last = sp.pop()
                    self.values[i] = self.convert(sp.pop())
            except socket.error as e: pass
            self.appendToSignal(self.values[i], "OUT%d" % (i + 1))


        
