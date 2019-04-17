#!/usr/bin/python

import csv
import yaml
import os
import argparse
from api import CoinBaseAPI

parser = argparse.ArgumentParser(description='Coinase metrics for i3blocks')
parser.add_argument('--toggle', action='store_true')
args = parser.parse_args()

click = os.environ.get('BLOCK_BUTTON', '0')
if click in '13':
    args.toggle = True

dirPath = os.path.dirname(os.path.realpath(__file__))+'/'
api_cfg = {}
with open(dirPath+'api_config.yaml') as f:
    api_cfg = yaml.load(f)

api = CoinBaseAPI(api_cfg['key'], api_cfg['secret'], api_cfg['version'])


def prettyFmt(BTC, ETH, LTC):
    colorise = lambda x: '<span foreground="#00FF00">{0}</span>'.format(x)
    colorisedCoins = list(map(colorise, [BTC, ETH, LTC]))
    return ':{0} Ξ:{1} Ł:{2}'.format(*colorisedCoins)

def getSpotPrices():
    LTCSpot = api.getSpotPrice('LTC')['amount']
    BTCSpot = api.getSpotPrice('BTC')['amount']
    ETHSpot = api.getSpotPrice('ETH')['amount']
    return BTCSpot, ETHSpot, LTCSpot

def getROIs():
    initialInvestment = {}
    with open(dirPath+'transaction_log.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            currency = row['currency']
            if currency in initialInvestment:
                initialInvestment[currency] += float(row['price'])
            else:
                initialInvestment[currency] = float(row['price'])

    accounts = api.getAccounts()

    btc, eth, ltc = getSpotPrices()
    spotPrices = {'BTC': float(btc), 'ETH': float(eth), 'LTC': float(ltc)}

    currentPrice = {}
    for wallet in accounts:
        currency = wallet['currency']['code']

        if currency == 'GBP': continue

        if currency in spotPrices:
            if currency in currentPrice:
                currentPrice[currency] += float(wallet['balance']['amount']) * spotPrices[currency]
            else:
                currentPrice[currency] = float(wallet['balance']['amount']) * spotPrices[currency]

    def roi(initial, current):
        return round(((current / initial)-1)*100,2)

    rois = {}
    for currency, value in currentPrice.items():
        if currency in initialInvestment:
            cost = initialInvestment[currency]
            rois[currency] = roi(cost, value)

    return prettyFmt(rois['BTC'], rois['ETH'], rois['LTC'])

with open(dirPath+'.STATE') as statefile:
    state = statefile.read()

if args.toggle == True:
    with open(dirPath+'.STATE', 'w') as statefile:
        if state == 'ROI':
            statefile.write('PRICE')
            state = 'Price'
        else:
            statefile.write('ROI')
            state = 'ROI'

    args.toggle = False

if state == 'ROI':
    print(getROIs())
else:
    BTCSpot, ETHSpot, LTCSpot = getSpotPrices()
    print(prettyFmt(BTCSpot, ETHSpot, LTCSpot))
