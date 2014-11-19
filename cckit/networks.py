import sys


class Wrapper(object):
    pass

sys.modules[__name__] = Wrapper
