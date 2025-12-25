import os
from dotenv import load_dotenv

load_dotenv()


BASE_CURRENCY = "usd"
DATA_DIR = "data/"
HOLDINGS_FILE = f"{DATA_DIR}holdings.csv"
SNAPSHOT_FILE = f"{DATA_DIR}portfolio_snapshot.csv"

WEI_IN_ETH = 10**18


ETH_RPC_URL = os.getenv("ETH_RPC_URL")
ARB_RPC_URL = os.getenv("ARB_RPC_URL")
BASE_RPC_URL = os.getenv("BASE_RPC_URL")
OPTIMISM_RPC_URL = os.getenv("OPTIMISM_RPC_URL")
BSC_RPC_URL = os.getenv("BSC_RPC_URL")
POLYGON_RPC_URL = os.getenv("POLYGON_RPC_URL")
AVALANCHE_RPC_URL = os.getenv("AVALANCHE_RPC_URL")


ENABLE_ALCHEMY = bool(os.getenv("ALCHEMY_API_KEY"))
