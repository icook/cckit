A basic POC for a sufficiently generic Crypto network defintion. Basic
interface can be demonstrated:

```
>>> from cckit.networks import Bitcoin
# The Transaction object has a reference to it's Network configuration
>>> print(Bitcoin.transaction)
<class 'cckit._networks.BitcoinTransaction'>
>>> print(Bitcoin.transaction.network)
<class 'cckit._networks.Bitcoin'>
# A new Network can inherit from Bitcoin, but now gets it's own object classes
# that link back to the correct Network configuration
>>> class Litecoin(Bitcoin):
...     pass
... 
>>> print(Litecoin.transaction)
<class 'cckit._networks.LitecoinTransaction'>
>>> print(Litecoin.transaction.network)
<class '__main__.Litecoin'>
>>> Litecoin.transaction().test()
this is a test
>>> Bitcoin.transaction().test()
this is a test
# The newly defined network is automatically available in the expected import
>>> from cckit.networks import Litecoin
>>> print(Litecoin.transaction)
<class 'cckit._networks.LitecoinTransaction'>
```

Motivation
----------
Generic network objects can now access the network parameters they need easily
by referencing ``self.network.<parameter>`` and it will get the correct
parameter without use of globals or explicit declaration. In addition, new
Network objects can be defined outside of the module and are instantly
available and referenceable inside the module.
