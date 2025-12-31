# Crypto Portfolio Tracker (Multi-Chain, On-Chain Accurate)

A self-hosted, multi-chain cryptocurrency portfolio tracker built with Python/Flask that aggregates on-chain wallet balances across major EVM networks, with real-time pricing data, aggressively filters scam/dust tokens, and presents a clean, accurate portfolio summary.

## ✨ Features

### Multi-Chain Support
Supports all major EVM chains:

- Ethereum
- Arbitrum
- Optimism
- Polygon
- Base
- Binance Smart Chain (BSC)

Chains are dynamically enabled based on available RPC endpoints (public fallbacks included).

### Accurate Token Balances
- Native token balances fetched via direct RPC calls
- ERC-20 / BEP-20 balances fetched via Alchemy (where supported) or fallback RPC
- SQLite caching for fast reloads and rate-limit protection

### Price Resolution
Prices are resolved using a robust tiered strategy:

1. **Native tokens**  
   - ETH (all L2s + mainnet): CoinGecko (reliable, consistent)  
   - BNB (BSC): CoinGecko  
   - POL (Polygon): GeckoTerminal DEX pools

2. **ERC-20 tokens**  
   - Direct DEX-based pricing via GeckoTerminal (best for real liquidity)

3. **Stablecoin fallback**  
   - USDC / USDT / DAI / etc. → fixed at $1.00

4. **Safety guards**  
   - Value capping (absurd prices limited)  
   - Dust filtering (holdings < $1 hidden)  
   - Scam token detection & removal


### Filtering & Cleanup
- Aggressive scam token detection (XETH, ETHG, airdrop scams, etc.)
- Dust filtering (< $1 value)
- Deduplication of same-token holdings across chains
- Stablecoin normalization

### UI
- Lightweight Flask frontend (no heavy JS frameworks)
- Responsive table showing:
  - Asset
  - Chain
  - Quantity
  - Value (USD)
- Export to CSV functionality
- Save snapshot button for historical tracking

### Efficient & Cached
- SQLite-backed caching for:
  - Wallet balances per chain
  - Token metadata
  - Price lookups
- Avoids hammering APIs/RPCs on repeated loads


## How Pricing Works

Prices are resolved in priority order:

1. Native chain pricing (ETH, BNB, POL) → CoinGecko for reliability
2. ERC-20 token price → GeckoTerminal (real DEX liquidity)
3. Stablecoin fallback → $1.00
4. No price → token excluded from total value (prevents misleading inflation)

This avoids:
- Fake/scam tokens with manipulated pools
- Zero-liquidity junk inflating totals
- Inconsistent L2 pricing


## ⚠️ Known Limitations

- Tokens without reliable liquidity will show $0 or be filtered
- BSC currently shows only native BNB (Alchemy does not support BEP-20 balances)
- No NFT valuation (by design — on-chain tokens only)
- No staking/LP/locked position detection yet
- No historical PnL charts (snapshots saved for future use)

## 🔮 Future Enhancements (Roadmap)

- Full BEP-20 support via alternative provider (Covalent/Moralis)
- Liquidity pool & staking position detection
- Token logos & metadata enrichment
- Historical portfolio charts
- Multi-wallet support & tagging
- PDF/CSV export improvements
- Dark mode toggle

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- `git`, `pip`, `virtualenv`

### Installation & Run

```bash
git clone https://github.com/Alpha-M2/crypto-portfolio-tracker.git
cd crypto-portfolio-tracker
```

# Setup virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

# Run
```bash
python app.py
```

## LicenseMIT 

License — free to use, modify, and distribute.

