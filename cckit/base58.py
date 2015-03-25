from hashlib import sha256


B58_ALPHA = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
B58_BASE = len(B58_ALPHA)
B58_MAPPING = {c: i for i, c in enumerate(B58_ALPHA)}


def b58decode(val, length):
    """
    Decode a Base58 value to bytes.

    Note: not tested in Python 2
    """
    n = 0
    for char in val:
        n *= B58_BASE
        try:
            n += B58_MAPPING[char]
        except KeyError:
            raise ValueError("Non-Base58 character: '{}'".format(char))
    return n.to_bytes(length, 'big')


def _parse_address(str_address):
    bytes = b58decode(str_address, 25)
    if bytes is None:
        raise AttributeError("'{}' is invalid base58 of decoded length 25"
                             .format(str_address))
    version = bytes[0]
    checksum = bytes[-4:]
    hash160 = bytes[:-4]
    hashed_checksum = sha256(sha256(hash160).digest()).digest()[:4]
    if hashed_checksum != checksum:
        raise AttributeError("'{}' has an invalid address checksum"
                             .format(str_address))

    return version, bytes[1:-4]


def get_bcaddress_version(str_address):
    """ Returns the address version of a bitcoin style address hash """
    try:
        return _parse_address(str_address)[0]
    except AttributeError:
        return None