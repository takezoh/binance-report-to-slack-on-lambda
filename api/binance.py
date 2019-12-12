import os
import time
import requests
import hashlib
import urllib
import hmac

API_DEBUG=False

API_KEY = os.environ['BINANCE_API_KEY']
API_SECRET = os.environ['BINANCE_API_SECRET']
ENDPOINT = "https://api.binance.com"
API_VERSION = 'v3'


class SecurityType():
    NONE = 0		# Endpoint can be accessed freely.
    TRADE = 1		# Endpoint requires sending a valid API-Key and signature.
    USER_DATA = 2	# Endpoint requires sending a valid API-Key and signature.
    USER_STREAM = 3	# Endpoint requires sending a valid API-Key.
    MARKET_DATA = 4	# Endpoint requires sending a valid API-Key.


class Client():
    def get_ticker_price(self):
        return self._get('ticker/price', security_type=SecurityType.NONE)

    def get_account(self):
        return self._get('account', security_type=SecurityType.USER_DATA)

    def _create_header(self, security_type=SecurityType.NONE, **kwargs):
        if security_type == SecurityType.NONE:
            return {}
        return {
            'X-MBX-APIKEY': API_KEY,
            }

    def _create_payload(self, security_type=SecurityType.NONE, **params):
        require_signature = security_type in (SecurityType.TRADE, SecurityType.USER_DATA)
        if require_signature:
            params['timestamp'] = str(int(time.time() * 1000 - 1500))

        if not params:
            return None
        
        payload = '&'.join([k + '=' + urllib.parse.quote(v.encode('utf-8')) for k, v in params.items()])
        if not require_signature:
            return payload

        signature = hmac.new(API_SECRET.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()
        return payload + '&signature=' + signature

    def _get(self, path, **params):
        headers = self._create_header(**params)
        payload = self._create_payload(**params)
        r = requests.get(ENDPOINT + "/api/{}/{}".format(API_VERSION, path), headers=headers, params=payload, verify=API_DEBUG)
        r.raise_for_status()
        return r.json()
