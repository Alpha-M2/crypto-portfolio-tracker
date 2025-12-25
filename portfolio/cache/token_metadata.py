import json
import os
from typing import Dict

CACHE_FILE = "data/token_metadata.json"


def load_token_cache() -> Dict[str, dict]:
    """
    Load cached ERC-20 token metadata.
    Format:
    {
        "0xabc...": {
            "symbol": "USDC",
            "decimals": 6
        }
    }
    """
    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_token_cache(cache: Dict[str, dict]) -> None:
    os.makedirs("data", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2, sort_keys=True)
