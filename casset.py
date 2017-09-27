import csv
import yaml
from api import CoinBaseAPI

initialInvestment = {}
with open('transaction_log.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        currency = row['currency']
        if currency in initialInvestment:
            initialInvestment[currency] += float(row['price'])
        else:
            initialInvestment[currency] = float(row['price'])

print(initialInvestment)

api_cfg = {}
with open('api_config.yaml') as f:
    api_cfg = yaml.load(f)

api = CoinBaseAPI(api_cfg['key'], api_cfg['secret'], api_cfg['version'])
accounts = api.getAccounts()

currentPrice = {}
for wallet in accounts:
    currency = wallet['currency']['code']
    if currency in currentPrice:
        currentPrice[currency] += float(wallet['native_balance']['amount'])
    else:
        currentPrice[currency] = float(wallet['native_balance']['amount'])

print(currentPrice)

def roi(initial, current):
    return ((current / initial)-1)*100

rois = {}
for currency, value in currentPrice.items():
    if currency in initialInvestment:
        cost = initialInvestment[currency]
        rois[currency] = roi(cost, value)

print(rois)
r = api.getBuyPrice('LTC')['amount']
print(r)
