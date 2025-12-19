import os

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
BASE_CURRENCY = "usd"

DATA_DIR = "data/"
HOLDINGS_FILE = DATA_DIR + "holdings.csv"
SNAPSHOT_FILE = DATA_DIR + "portfolio_snapshot.csv"

WEI_IN_ETH = 10**18

ALCHEMY_ETH_RPC_URL = os.getenv("ALCHEMY_ETH_RPC_URL")
