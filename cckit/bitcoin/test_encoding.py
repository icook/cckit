import pytest

from . import encoding


int_tests = [
    (b'\xfc', 252),
    (b'\xfd\xff\xff', (2 ** 16-1)),
    (b'\xfe\xff\xff\xff\xff', (2 ** 32-1)),
    (b'\xff\xff\xff\xff\xff\xff\xff\xff\xff', (2 ** 64-1)),
]


@pytest.mark.parametrize("encoded,decoded", int_tests)
def test_int_decode(encoded, decoded):
    assert encoding.Int.from_bytes(encoded) == decoded


@pytest.mark.parametrize("encoded,decoded", int_tests)
def test_int_encode(encoded, decoded):
    int_obj = encoding.Int(decoded)
    print(int_obj)
    assert int_obj.to_bytes() == encoded


string_tests = [
    (b'\x0bthisisatest', b'thisisatest'),
]


@pytest.mark.parametrize("encoded,decoded", string_tests)
def test_string_decode(encoded, decoded):
    assert encoding.String.from_bytes(encoded) == decoded


@pytest.mark.parametrize("encoded,decoded", string_tests)
def test_string_encode(encoded, decoded):
    str_obj = encoding.String(decoded)
    print(str_obj)
    assert str_obj.to_bytes() == encoded


hash_tests = [
    (b'\xfb\xff\xff\xfa\xff\xfc\xff\xbf\xfb\xff\xff\xfa\xff\xfc\xff\xbf\xfb\xff\xff\xfa\xff\xfc\xff\xbf\xfb\xff\xff\xfa\xff\xfc\xff\xbf'),
]


@pytest.mark.parametrize("bytes", hash_tests)
def test_hash_recode(bytes):
    obj = encoding.Hash.from_rpc_bo(bytes)
    assert obj.rpc_bo == bytes
    obj2 = encoding.Hash.from_internal_bo(bytes)
    assert obj2.internal_bo == bytes

    assert obj2.rpc_bo == obj.internal_bo
    assert obj2.internal_bo == obj.rpc_bo
