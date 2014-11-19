from . import bitcoin
from . import networks


class NetworkMetaclass(type):
    def __init__(cls, name, bases, dct):
        cls_name = cls.__name__
        setattr(networks, cls_name, cls)
        for attr_name, attr in dct.items():
            if hasattr(attr, "network"):
                new_type = type(cls_name + attr.__name__, (attr, ), {})
                new_type.network = cls
                setattr(cls, attr_name, new_type)
        super(NetworkMetaclass, cls).__init__(name, bases, dct)


class Network(object):
    __metaclass__ = NetworkMetaclass


class Bitcoin(Network):
    transaction = bitcoin.Transaction
