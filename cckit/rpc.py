import base64
import json
import decimal
import urllib3
# Support Python2/3 changed core lib names
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

# Connection/response error constants
RPC_UNKN_CONN_ERROR = -1, "HTTP exception thrown in connection handling"
RPC_MAX_RETRIES_EXCEEDED_ERROR = -2, "Max connection attempts exceeded"
RPC_READ_TIMEOUT_ERROR = -3, "Max time spent waiting for a response exceeded"
RPC_NO_RESPONSE = -4, "missing HTTP response from server"
RPC_NOT_JSON_ERROR = -5, "Response type not JSON (typically from auth failure)"
RPC_RESPONSE_NO_CODE = -6, "JSON-RPC response missing error code"
RPC_RESPONSE_MISSING_RESULT = -7, "JSON-RPC response missing result"


class CoinRPCException(Exception):
    def __init__(self, error):
        self.error = error
        if isinstance(error, tuple):
            self.code, self.rpc_error = error
        super(CoinRPCException, self).__init__(str(self.error))


class CoinRPC(object):
    """
    Interact with a Coin server's JSON RPC directly. No conversion is done
    from the coin's JSON response objects outside of deserialization.

    This class is intentionally API agnostic, and should be usable by all
    Coins which use a JSON RPC spec similar to bitocin core. It is designed to
    be inherited in order to build a Coin specific API wrapper.

    Example usage::

        # Setup
        user = 'litecoinrpc'
        pwd = 'testing'
        addr = 'localhost'
        port = 12345
        rpc = CoinRPC("http://{0}:{1}@{2}:{3}/".format(user, pwd, addr, port))

        # Single call
        rpc.getinfo()

        # Batched calls
        methods = [{'getbalance': []},{'getbalance': []}]
        rpc.batch(methods)
    """

    def __init__(self, service_url, http_pool_kwargs=None, http_headers=None):
        """
        :param service_url: The http connection URL to a Coin server.
        :type service_url: str
        :param http_pool_kwargs: Updates HTTP pool setup defaults
        :type http_pool_kwargs: dict
        :param http_headers: Updates HTTP header defaults
        :type http_headers: dict
        :returns:  None
        :raises: TypeError, ValueError
        """

        # Basic input checking
        if not service_url:
            raise ValueError('Service url is required')
        else:
            service_url = str(service_url)
        if http_pool_kwargs and not isinstance(http_pool_kwargs, dict):
            raise TypeError('pool_kwargs type must be dictionary')
        if http_headers and not isinstance(http_headers, dict):
            raise TypeError('http_headers type must be dictionary')

        # Parse connection data
        self._id_count = 0
        self._url = urlparse.urlparse(service_url)
        self._use_ssl = True if self._url.scheme == 'https' else False
        if self._url.port is None:
            self._url.port = 443 if self._use_ssl else 80
        authpair = "{}:{}".format(self._url.username, self._url.password)
        authpair = authpair.encode('utf8')
        http_auth = b"Basic " + base64.b64encode(authpair)

        # Setup HTTP header defaults & configuration
        self.http_headers = {'Host': self._url.hostname,
                             'User-Agent': "CoinRPC/0.1",
                             'Authorization': http_auth,
                             'Content-type': 'application/json'}
        if http_headers:
            self.http_headers.update(http_headers)

        # Configure & instantiate the HTTP connection pool
        self.http_pool_kwargs = dict(host=self._url.hostname,
                                     port=self._url.port,
                                     timeout=60,
                                     headers=self.http_headers,
                                     maxsize=5,
                                     block=True)
        if http_pool_kwargs:
            self.http_pool_kwargs.update(http_pool_kwargs)

        pool_cls = urllib3.HTTPSConnectionPool if self._use_ssl else \
            urllib3.HTTPConnectionPool
        self._conn = pool_cls(**self.http_pool_kwargs)

    def __getattr__(self, name):
        """
        Build & return a function to make a RPC call of the same name

        :returns:  A execute function to make the desired RPC function
        :raises: AttributeError
        """
        # Ignore private attrs
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError
        # Build callable
        c = lambda *args: self.call(name, *args)
        # Preserve our function name
        c.__name__ = name
        return c

    def __call__(self, *args):
        """Wraps call"""
        return self.call(*args)

    def call(self, service_name, *args):
        """
        Make an HTTP request to the Coin RPC for the method <service_name>

        :param service_name: The method to run on the RPC
        :type service_name: str
        :param args: Args to be passed with the RPC call
        :type args: args
        :returns:  The HTTP response
        :raises: CoinRPCException
        """
        self._id_count += 1
        postdata = json.dumps({"jsonrpc": "2.0",
                               'method': service_name,
                               'params': args,
                               'id': self._id_count})

        response = self._get_response(postdata)
        self._check_response(response)
        return response['result']

    def batch(self, method_list):
        """
        Make multiple RPC calls in a single HTTP request

        :param method_list: A list of call dictionaries. Ala [{'method':[args]}]
        :type method_list: list
        :returns:  A list of the responses
        :raises: CoinRPCException
        """
        batch_data = []
        for call_dict in method_list:
            self._id_count += 1
            for m, args in call_dict.items():
                batch_data.append({"jsonrpc": "2.0",
                                   "method": m,
                                   "params": args,
                                   "id": self._id_count})

        postdata = json.dumps(batch_data)
        responses = self._get_response(postdata)
        results = []
        for response in responses:
            self._check_response(response)
            results.append(response['result'])
        return results

    def _get_response(self, postdata):
        """
        Given some post data, make a request, parse it, return the response

        :param postdata: A JSON serialized dictionary to post
        :type postdata: list
        :returns:  The HTTP response
        :raises: CoinRPCException, ValueError
        """
        try:
            response = self._conn.urlopen('POST', self._url.path, postdata)
        except urllib3.exceptions.MaxRetryError:
            raise CoinRPCException(RPC_MAX_RETRIES_EXCEEDED_ERROR)
        except urllib3.exceptions.ReadTimeoutError:
            raise CoinRPCException(RPC_READ_TIMEOUT_ERROR)
        except urllib3.exceptions.HTTPError as e:
            msg = "{}: {}".format(RPC_UNKN_CONN_ERROR[1], e)
            raise CoinRPCException((RPC_UNKN_CONN_ERROR[0], msg))

        if response is None:
            raise CoinRPCException(RPC_NO_RESPONSE)

        try:
            response = json.loads(response.data.decode('utf8'),
                                  parse_float=decimal.Decimal)
        except ValueError:
            raise CoinRPCException(RPC_NOT_JSON_ERROR)
        return response

    def _check_response(self, response):
        """
        Checks a Coin server's JSON response for expected values

        :param response: The response JSON to check
        :type response: dict
        :returns:  None
        :raises: CoinRPCException
        """
        if 'error' not in response:
            raise CoinRPCException(RPC_RESPONSE_NO_CODE)

        if response['error'] is not None:
            raise CoinRPCException((response['error']['code'],
                                    response['error']['message']))
        elif 'result' not in response:
            raise CoinRPCException(RPC_RESPONSE_MISSING_RESULT)
