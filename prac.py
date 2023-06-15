import socket

class BaseClient:
    def __init__(self, timeout:int=10, buffer:int=1024):    # timeout in seconds
        self.__socket = None    # socket object
        self.__address = None   # address of server
        self.__timeout = timeout    # timeout in seconds
        self.__buffer = buffer  # buffer size in bytes

    def connect(self, address, family:int, typ:int, proto:int): # family: AF_INET, AF_INET6, AF_UNIX; typ: SOCK_STREAM, SOCK_DGRAM, SOCK_RAW
        self.__address = address    # address of server
        self.__socket = socket.socket(family, typ, proto)   # create socket object
        self.__socket.settimeout(self.__timeout)    # set timeout
        self.__socket.connect(self.__address)   # connect to server

    def send(self, message:str="") -> None: # send message to server
        flag = False
        while True:
            in1 = self.__socket.recv(self.__buffer).decode('utf-8')
            self.received(in1)
            message_send = "dc_ok"
            self.__socket.send(message_send.encode('utf-8'))
            print("aaa")
            message_recv = self.__socket.recv(self.__buffer).decode('utf-8')
            self.received(message_recv)
            if flag:
                break
        try:
            self.__socket.shutdown(socket.SHUT_RDWR)
            self.__socket.close()
        except:
            pass

    def received(self, message:str):
        print(message)

class InetClient(BaseClient):
    def __init__(self, host:str="dc3-server", port:int=10000) -> None:
        self.server=(host,port)
        super().__init__(timeout=60, buffer=1024)
        super().connect(self.server, socket.AF_INET, socket.SOCK_STREAM, 0)

if __name__=="__main__":
    cli = InetClient()
    cli.send()

