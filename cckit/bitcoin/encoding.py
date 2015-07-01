import struct
import binascii
import sys

from ..serialize import Streamer
from hashlib import sha256
if sys.version_info[0] >= 3:
    integer_class = int
else:
    integer_class = long


class Int(Streamer, integer_class):
    """ Encoding for a variable length integer. Read more about it here:
    https://en.bitcoin.it/wiki/Protocol_specification#Variable_length_integer
    """
    @classmethod
    def from_stream(cls, f):
        prefix = ord(f.read(1))
        if prefix == 253:
            return struct.unpack("<H", f.read(2))[0]
        if prefix == 254:
            return struct.unpack("<L", f.read(4))[0]
        if prefix == 255:
            return struct.unpack("<Q", f.read(8))[0]
        return prefix

    def to_stream(self, f):
        if self < 253:
            f.write(struct.pack("<B", self))
        elif self <= 65535:
            f.write(b'\xfd' + struct.pack("<H", self))
        elif self <= 0xffffffff:
            f.write(b'\xfe' + struct.pack("<L", self))
        else:
            f.write(b'\xff' + struct.pack("<Q", self))


class String(Streamer, bytes):
    """ Encoding for a variable length string. Read more about it here:
    https://en.bitcoin.it/wiki/Protocol_documentation#Variable_length_string
    """
    @classmethod
    def from_stream(cls, f):
        length = Int.from_stream(f)
        return cls(f.read(length))

    def to_stream(self, f):
        Int(len(self)).to_stream(f)
        f.write(self)


def to_bytes(v, length, byteorder="big"):
    l = bytearray()
    for i in range(length):
        mod = v & 0xff
        v >>= 8
        l.append(mod)
        if byteorder == "big":
            l.reverse()
    return bytes(l)


class Hash(integer_class):
    """ Helper object for dealing with hash encoding. Most functions from
    bitcoind deal with little-endian values while most consumer use
    big-endian. """
    @classmethod
    def from_le(cls, data):
        return cls(binascii.hexlify(data[::-1]), 16)

    @classmethod
    def from_be(cls, data):
        return cls(binascii.hexlify(data), 16)

    @property
    def le(self):
        return to_bytes(self, 32, byteorder="little")

    @property
    def be(self):
        return to_bytes(self, 32, byteorder="big")

    @classmethod
    def from_sha256d(cls, data):
        return cls.from_be(sha256(sha256(data).digest()).digest())
