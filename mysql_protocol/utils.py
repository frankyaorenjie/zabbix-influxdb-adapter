import binascii
import struct
import hashlib
from functools import partial

sha_new = partial(hashlib.new, 'sha1')


class Utils(object):
    @staticmethod
    def has_eof(packet):
        return packet[-5] == 254

    @staticmethod
    def is_error_packet(packet):
        return packet[4] == 255

    @staticmethod
    def is_ok_packet(packet):
        return packet[0] == 7 and packet[4] == 0

    @staticmethod
    def packet_number(packet):
        return packet[3]

    @staticmethod
    def socket_forward(src_s, dst_s):
        dst_s.send(src_s.recv(4096))

    @staticmethod
    def payload2Stmt(payload):
        return payload[5:].decode('utf-8')

    @staticmethod
    def scramble(password, salt):
        if not password:
            return b''
        stage1 = sha_new(password).digest()
        stage2 = sha_new(stage1).digest()
        result = sha_new(salt + stage2).digest()
        return binascii.hexlify(Utils.xor(result, stage1))

    @staticmethod
    def xor(message1, message2):
        length = len(message1)
        result = b''
        for i in range(length):
            x = (struct.unpack('B', message1[i:i + 1])[0] ^
                 struct.unpack('B', message2[i:i + 1])[0])
            result += struct.pack('B', x)
        return result


if __name__ == '__main__':
    s = Utils.scramble('CT=mpCxEfcu3i6'.encode(), '_89U$M;{}"/d.T=tPqkF'.encode())
    r = binascii.hexlify(s)
    print(r)
