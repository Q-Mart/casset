import csv
import yaml
from api import CoinBaseAPI

rows = []
with open('transaction_log.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        rows.append(row)

print(rows)

api_cfg = {}
with open('api_config.yaml') as f:
    api_cfg = yaml.load(f)

api = CoinBaseAPI(api_cfg['key'], api_cfg['secret'], api_cfg['version'])
r = api.getAccounts()
print(r.json())
