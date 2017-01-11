import socket
from mysql_protocol.utils import Utils

MYSQL_HOST = '10.3.99.100'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'CT=mpCxEfcu3i6'


class FakeMySQLServer(object):
    def __init__(self, host='localhost', port=3306):
        self._host = host
        self._port = port
        self._mysql_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._mysql_socket.connect((MYSQL_HOST, MYSQL_PORT))

    def close(self):
        self._mysql_socket.close()

    def foo(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self._host, self._port))
        s.listen(1)
        while True:
            client_sc, client_addr = s.accept()
            # Greeting
            Utils.socket_forward(self._mysql_socket, client_sc)
            # Login
            Utils.socket_forward(client_sc, self._mysql_socket)
            # Response OK
            Utils.socket_forward(self._mysql_socket, client_sc)
            # payload = b''
            while True:
                payload = client_sc.recv(4096)
                # not query
                if payload[3] != 0:
                    while True:
                        if Utils.has_eof(payload):
                            break
                        # p = client_sc.recv(4096)
                        payload += client_sc.recv(4096)
                if len(payload) == 0:
                    continue
                stmt = Utils.payload2Stmt(payload)
                print(stmt)
                self._mysql_socket.send(payload)
                mysql_payload = self._mysql_socket.recv(4096)
                print(mysql_payload)
                if not Utils.is_ok_packet(mysql_payload) and not Utils.is_error_packet(mysql_payload):
                    if mysql_payload[3] != 0:
                        while True:
                            if Utils.has_eof(mysql_payload):
                                break
                            # p = client_sc.recv(4096)
                            mysql_payload += self._mysql_socket.recv(4096)
                client_sc.send(mysql_payload)
                # Todo
                # if 'history' not in stmt:
                #     self._mysql_socket.send(payload)
                #     mysql_payload = self._mysql_socket.recv(4096)
                #     client_sc.send(mysql_payload)
                # else:
                #     print('haha, hook it')


if __name__ == '__main__':
    fake_mysql = FakeMySQLServer()
    fake_mysql.foo()
