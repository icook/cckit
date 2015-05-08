import struct

from ..serialize import Streamer
import sys
if sys.version[0] == 3:
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
