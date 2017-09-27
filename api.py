import hmac
import hashlib
import time
import requests
import errors


class CoinbaseWalletAuth(requests.auth.AuthBase):
    def __init__(self, api_key, api_secret, timestamp):
        self.__key = api_key
        self.__secret = bytes(api_secret, 'latin_1')
        self.__timestamp = timestamp

    def __call__(self, request):
        message = self.__timestamp + request.method + request.path_url + (request.body or '')
        signature = hmac.new(self.__secret, bytes(message, 'latin-1'), hashlib.sha256).hexdigest()

        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': self.__timestamp,
            'CB-ACCESS-KEY': self.__key,
        })
        return request

class CoinBaseAPI:

    def __requiresAuth(request):
        def wrapper(self):
            self.__requestRequiresAuth = True
            r = request(self)
            self.__requestRequiresAuth = False
            return r
        return wrapper

    def __init__(self, api_key, api_secret, api_version):
        self.__URL = 'https://api.coinbase.com/v2/'
        self.__headers = {'CB-VERSION': api_version}
        self.__requestRequiresAuth = False

        timestamp = str(self.getTime()['epoch'])
        self.__auth = CoinbaseWalletAuth(api_key, api_secret, timestamp)

    def __makeRequest(self, endpoint):
        if self.__requestRequiresAuth:
            return requests.get(self.__URL + endpoint, headers=self.__headers, auth=self.__auth)
        else:
            return requests.get(self.__URL + endpoint, params=None, headers=self.__headers)

    def __getData(self, endpoint):
        r = self.__makeRequest(endpoint)
        if r.status_code != 200: raise errors.ApiError("Status code of request is not 200")
        return r.json()['data']

    @__requiresAuth
    def getAccounts(self):
         return self.__getData('accounts')

    def getTime(self):
        return self.__getData('time')

    def getBuyPrice(self, currency):
        return self.__getData('prices/'+currency+'-GBP/buy')
