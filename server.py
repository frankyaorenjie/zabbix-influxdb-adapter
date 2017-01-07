import socket
import signal
import os
import binascii


class FakeMySQLServer(object):
    def __init__(self, host='localhost', port=3306):
        self._host = host
        self._port = port

    def foo(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self._host, self._port))
        s.listen(1)
        while True:
            client_sc, client_addr = s.accept()
            print(client_sc, client_addr)
            # signal.signal(signal.SIGCHLD, reap)
            x = b'4a0000000a352e362e33320001aa2d014e5e70386470286f00fff72102007f8015000000000000000000007b3c567c2e6e63232429414c006d7973716c5f6e61746976655f70617373776f726400'
            print('send done')
            client_sc.send(binascii.a2b_hex(x))
            while True:
                data = client_sc.recv(4096)
                if len(data) == 0:
                    break
                print(data)
                x = b'4a0000000a352e362e33320001aa2d014e5e70386470286f00fff72102007f8015000000000000000000007b3c567c2e6e63232429414c006d7973716c5f6e61746976655f70617373776f726400'
                print('send done')
                client_sc.send(x)


if __name__ == '__main__':
    fake_mysql = FakeMySQLServer(port=9009)
    fake_mysql.foo()