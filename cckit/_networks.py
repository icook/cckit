from . import bitcoin
from . import networks


class NetworkMetaclass(type):
    def __init__(cls, name, bases, dct):
        cls_name = cls.__name__

        # Don't actually use bases, just grab their attributes for a one time
        # copy. Kinda weird, but works for intended functionality.
        new_dct = {}
        for base in bases:
            new_dct.update(base.__dict__)
        new_dct.update(dct)
        bases = (object,)

        # Make the network class importable from our central import location
        setattr(networks, cls_name, cls)
        for attr_name, attr in new_dct.items():
            # If we're inheriting from something that already wrapped their
            # classes
            if hasattr(attr, "_wrapped_type"):
                attr = attr._wrapped_type

            # If it's a Network specific object type, create a wrapper class
            # that carries around the correct network reference
            if hasattr(attr, "network"):
                new_type = type(cls_name + attr.__name__, (attr, ), {})
                new_type.network = cls
                # Set a reference to the wrapped class for inheritence
                new_type._wrapped_type = attr
                setattr(cls, attr_name, new_type)

        super(NetworkMetaclass, cls).__init__(name, bases, new_dct)


Network = NetworkMetaclass('Network', (object,), {})


class Bitcoin(Network):
    transaction = bitcoin.Transaction
