import struct

from .encoding import String, Int, Hash
from cckit.rpc import CoinRPC


class Input(object):
    """ An individual input to a transaction. """

    def __init__(self):
        self.prevout_hash = Int(-1)
        self.prevout_idx = Int(-1)
        self.script_sig = String()
        self.seqno = Int(-1)

    @classmethod
    def from_stream(cls, f):
        self = cls()
        self.prevout_hash = Hash.from_le(f.read(32))
        self.prevout_idx, = struct.unpack("<L", f.read(4))
        self.script_sig = String.from_stream(f)
        self.seqno, = struct.unpack("<L", f.read(4))
        return self

    def to_stream(self, f):
        f.write(self.prevout_hash.le)
        f.write(struct.pack("<L", self.prevout_idx))
        self.script_sig.to_stream(f)
        f.write(struct.pack("<L", self.seqno))


class Output(object):
    """ script_pub_key is a byte string. Amount is an integer. """
    @classmethod
    def from_stream(cls, f):
        self = cls()
        self.amount, = struct.unpack("<Q", f.read(8))
        self.script_sig = String.from_stream(f)
        return self

    def to_stream(self, f):
        f.write(struct.pack("<Q", self.amount))
        self.script_sig.to_stream(f)


class Transaction(object):
    network = None

    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.locktime = 0
        self.version = 1

    def to_network(self, f):
        """ Writes the network stream to a bytestream """
        f.write(struct.pack("<L", self.version))
        Int(len(self.inputs)).to_stream(f)
        for inpt in self.inputs:
            inpt.to_stream(f)
        Int(len(self.outputs)).to_stream(f)
        for output in self.outputs:
            output.to_stream(f)
        f.write(struct.pack("<L", self.locktime))

    @classmethod
    def from_network(cls, f):
        """ Should take a network format Transaction message in and decode it
        into an object """
        self = cls()
        self.version, = struct.unpack("<L", f.read(4))
        input_count = Int.from_stream(f)
        self.inputs = []
        for i in range(input_count):
            self.inputs.append(Input.from_stream(f))
        output_count = Int.from_stream(f)
        self.outputs = []
        for i in range(output_count):
            self.outputs.append(Output.from_stream(f))
        self.locktime, = struct.unpack("<L", f.read(4))
        return self

    @classmethod
    def from_ref_disk(cls, f):
        """ Should take a reference client disk Transaction byte stream and
        decode it """
        return cls.from_network(f)


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
