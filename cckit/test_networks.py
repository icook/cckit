from . import networks


def test_int_encode():
    class Testcoin(networks.Bitcoin):
        pass

    assert Testcoin.transaction.__name__ == "TestcoinTransaction"
    assert Testcoin.transaction.network == Testcoin
