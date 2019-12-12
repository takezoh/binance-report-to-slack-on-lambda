import os
import json
import requests
from api.binance import Client as BinanceClient
from api.gmo import Client as GMOClient

SLACK_POST_URL = os.environ['SLACK_POST_URL']
STABLE_USD = 'BUSD'


def post_slack(assets, xrp_jpy):
    attachments = []
    for asset in assets:
        attachments.append({
            'title': asset['symbol'],
            'fields': [
                {
                    'title': 'Balance',
                    'value': '{:.8f}'.format(asset['balance']),
                    'short': True,
                },
                {
                    'title': '{} Rate'.format(asset['rate']['symbol']),
                    'value': '{:.8f}'.format(asset['rate']['value']),
                    'short': True,
                },
                {
                    'title': 'USD',
                    'value': '{:.3f}'.format(asset['usd']),
                    'short': True,
                },
                {
                    'title': 'XRP JPY',
                    'value': '{:.5f}'.format(asset['xrp'] * xrp_jpy),
                    'short': True,
                },
            ],
        })

    text = 'Binance Reports'

    payload = {
        'text': text,
        'attachments': attachments,
    }

    requests.post(SLACK_POST_URL, data=json.dumps(payload))


def get_asset_data(name, balance, prices):
    symbol = None
    usd = 0
    rate = 0

    if name == STABLE_USD:
        symbol = STABLE_USD
        usd = balance
        rate = 1
    elif name + STABLE_USD in prices:
        symbol = STABLE_USD
        rate = float(prices[name + STABLE_USD])
        usd = balance * rate
    else:
        symbol = 'BTC'
        rate = float(prices[name + symbol])
        btc = balance * rate
        usd = btc * float(prices['BTC' + STABLE_USD])

    xrp = 0
    if name == 'XRP':
        xrp = balance
    #  elif name + 'XRP' in prices:
        #  xrp = balance * float(prices[name + 'XRP'])
    elif 'XRP' + name in prices:
        xrp = balance / float(prices['XRP' + name])
    else:
        btc = balance * float(prices[name + 'BTC'])
        xrp = btc / float(prices['XRPBTC'])

    return {
        'symbol': name,
        'balance': balance,
        'usd': usd,
        'xrp': xrp,
        'rate': {
            'symbol': symbol,
            'value': rate,
        },
    }


def lambda_handler(event, context):
    client = BinanceClient()

    r = client.get_ticker_price()
    prices = {x['symbol']: x['price'] for x in r}

    assets = []

    r = client.get_account()
    for asset in r['balances']:
        balance = float(asset['free']) + float(asset['locked'])
        if balance > 0:
            assets.append(get_asset_data(asset['asset'], balance, prices))

    r = GMOClient().get_ticker('XRP_JPY')
    xrp_jpy = float(r['data'][0]['last'])

    post_slack(assets, xrp_jpy)

if __name__ == '__main__':
    lambda_handler(None, None)
