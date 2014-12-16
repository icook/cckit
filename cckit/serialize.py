import binascii

from io import BytesIO


class Streamer(object):
    @classmethod
    def from_hex(cls, hex_data):
        return cls.from_stream(BytesIO(binascii.unhexlify(hex_data)))

    @classmethod
    def from_bytes(cls, data):
        stream = BytesIO(data)
        ret = cls.from_stream(stream)
        if stream.tell() < (len(data) - 1):
            raise Exception("Didn't consume all bytes")
        return ret

    def to_hex(cls):
        return cls.to_stream().read()

    def to_bytes(cls):
        f = BytesIO()
        cls.to_stream(f)
        f.seek(0)
        return f.read()
