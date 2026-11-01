# Qwenn-RPC

Anvil/RPC integration for real-time market data.

## Maintainer
**codingsh <codingsh@pm.me>**

## Description
Fetch market data from Anvil/Ethereum RPC → QwenBend generation → strategy execution → results pipeline.

### Features
- ✅ Anvil RPC client for block number, timestamp, ETH price
- ✅ Market data processing for BendLite input
- ✅ Pipeline integration: RPC → Qwen generation → verification → engine
- ✅ JSON/CSV data persistence for backtesting

### RPC Endpoints
- Anvil local: http://127.0.0.1:8545
- eth_blockNumber, eth_getBlockByNumber, eth_getPrice (custom)

### Integration Flow
```
Anvil RPC Fetch → Data Processing → Qwen Strategy Generation → BendVM Verification → Engine Execution → Results + Trace
```

## Status
- [x] Anvil RPC client (concluído)
- [x] Market data processing (concluído)
- [x] Pipeline integration (concluído)
- [x] JSON/CSV persistence (concluído)
- [ ] Clanker integration (planejado)

## Tests
```
$ cd /Volumes/MASS/qwenn-rpc
$ python3 -m pytest tests/
# 10 tests passing
```

## Architecture
```
Qwenn-RPC
├── qwenn_rpc/              # RPC client modules
├── anvil_client.py         # Anvil RPC client
├── tests/                  # Test suite
├── pyproject.toml         # Project config
└── README.md              # This file
```

## Quick Start
```bash
# Install
pip install -r requirements.txt

# Fetch market data from Anvil
python3 -c "
from qwenn_rpc.anvil_client import fetch_block_data
data = fetch_block_data()
print(f'Block: {data[\"block\"]}')
print(f'Timestamp: {data[\"timestamp\"]}')
print(f'ETH Price: ${data[\"eth_price\"]}')
"
```

## Integration with Clanker
This RPC integration can be combined with Clanker token launcher for:
- Real-time market data for token launches
- Price feeds for AI droids
- On-chain data integration for tokenomics