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
