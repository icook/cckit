from cckit.rpc import CoinRPC


class Transaction(object):
    network = None

    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.locktime = 0
        self.version = 1

    @classmethod
    def from_network(cls, bytestream):
        """ Should take a network format Transaction message in and decode it
        into an object """
        return cls()

    @classmethod
    def from_ref_disk(cls, bytestream):
        """ Should take a reference client disk Transaction in and decode it
        """
        return cls()


class RPCWrapper(CoinRPC):
    """
    Creates a wrapper for a coin's JSON RPC response. Unlike CoinRPC
    its methods wrap coin specific RPC calls. Additionally, responses
    are returned as objects instead of JSON.

    .. note::
       Woefully incomplete atm - more of a proof of concept
    """
    network = None

    def __init__(self, service_url, **kwargs):
        super(RPCWrapper, self).__init__(service_url=service_url, **kwargs)

    def dump_priv_key(self, addr):
        """Return the private key matching the given address hash"""
        return self.dumpprivkey(addr)

    def get_account_address(self, account):
        """
        Return the current Coin address for receiving payments to this account,
        create the account if it does not exist.
        """
        return self.getaccountaddress(account)
