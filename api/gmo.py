import requests


PUBLIC_API = 'https://api.coin.z.com/public'
API_VERSION = 'v1'


class Client():

    def get_ticker(self, symbol=None):
        params = {}
        if symbol:
            params['symbol'] = symbol

        return self._get(PUBLIC_API, 'ticker', **params)

    def _get(self, api_type, path, **params):
        r = requests.get(api_type + '/{}/{}'.format(API_VERSION, path), params=params)
        r.raise_for_status()
        return r.json()
