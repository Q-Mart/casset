import hmac
import hashlib
import time
import requests

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

    def __init__(self, api_key, api_secret, api_version):
        self.__URL = 'https://api.coinbase.com/v2/'
        self.__headers = {'CB-VERSION': api_version}

        timestamp = str(self.getTime().json()['data']['epoch'])
        self.__auth = CoinbaseWalletAuth(api_key, api_secret, timestamp)

    def __makeRequest(self, endpoint, auth=True):
        if auth:
            return requests.get(self.__URL + endpoint, headers=self.__headers, auth=self.__auth)
        else:
            return requests.get(self.__URL + endpoint, params=None, headers=self.__headers)

    def getAccounts(self):
         return self.__makeRequest('accounts')

    def getTime(self):
        return self.__makeRequest('time', auth=False)
