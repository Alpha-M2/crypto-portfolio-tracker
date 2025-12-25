import os
from portfolio.wallets.alchemy import fetch_erc20_holdings


def test_alchemy_fetch():
    wallet = os.getenv("TEST_WALLET")
    assert wallet, "Set TEST_WALLET env var"

    tokens = fetch_erc20_holdings(wallet, "ethereum")
    assert isinstance(tokens, list)

    if tokens:
        t = tokens[0]
        assert hasattr(t, "contract_address")
        assert hasattr(t, "amount")
        assert t.is_erc20 is True
