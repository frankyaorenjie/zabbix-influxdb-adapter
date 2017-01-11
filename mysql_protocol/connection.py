import socket
from mysql_protocol.utils import Utils


class MySQLConnection(object):
    def __init__(self, host, port, user, password):
        self._mysql_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._mysql_socket.connect((host, port))
        greeting = self._mysql_socket.recv(4096)
        salt = greeting[16:24] + greeting[43:55]
        encrypt_password = Utils.scramble(password.encode(), salt)
        print(encrypt_password)

    def close(self):
        self._mysql_socket.close()



if __name__ == '__main__':
    m = MySQLConnection(host='10.3.99.100', port=3306, user='root', password='CT=mpCxEfcu3i6')
