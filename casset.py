#!/usr/bin/python

import csv
import yaml
import os
from api import CoinBaseAPI

dirPath = os.path.dirname(os.path.realpath(__file__))+'/'
api_cfg = {}
with open(dirPath+'api_config.yaml') as f:
    api_cfg = yaml.load(f)

api = CoinBaseAPI(api_cfg['key'], api_cfg['secret'], api_cfg['version'])


def prettyFmt(BTC, ETH, LTC):
    colorise = lambda x: '<span foreground="#00FF00">{0}</span>'.format(x)
    colorisedCoins = list(map(colorise, [BTC, ETH, LTC]))
    return ':{0} Ξ:{1} Ł:{2}'.format(*colorisedCoins)

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

    currentPrice = {}
    for wallet in accounts:
        currency = wallet['currency']['code']
        if currency in currentPrice:
            currentPrice[currency] += float(wallet['native_balance']['amount'])
        else:
            currentPrice[currency] = float(wallet['native_balance']['amount'])

    def roi(initial, current):
        return round(((current / initial)-1)*100,2)

    rois = {}
    for currency, value in currentPrice.items():
        if currency in initialInvestment:
            cost = initialInvestment[currency]
            rois[currency] = roi(cost, value)

    return prettyFmt(rois['BTC'], rois['ETH'], rois['LTC'])

def getSpotPrices():
    LTCSpot = api.getSpotPrice('LTC')['amount']
    BTCSpot = api.getSpotPrice('BTC')['amount']
    ETHSpot = api.getSpotPrice('ETH')['amount']
    return prettyFmt(BTCSpot, ETHSpot, LTCSpot)

with open(dirPath+'.STATE') as statefile:
    state = statefile.read()

with open(dirPath+'.STATE', 'w') as statefile:
    if state == 'ROI':
        print(getROIs())
        statefile.write('PRICE')
    else:
        print(getSpotPrices())
        statefile.write('ROI')
