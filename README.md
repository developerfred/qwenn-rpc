# Qwenn-RPC
Integração Anvil/RPC para dados de mercado em tempo real.

## Maintainer
**codingsh <codingsh@pm.me>**

## Description
Fetch market data from Anvil/Ethereum RPC → QwenBend generation → strategy execution → results pipeline.

## Features
- ✅ Anvil RPC client for block number, timestamp, ETH price
- ✅ Market data processing for BendLite input
- ✅ Pipeline integration: RPC → Qwen generation → verification → engine
- ✅ JSON/CSV data persistence for backtesting

## RPC Endpoints
- Anvil local: http://127.0.0.1:8545
- eth_blockNumber, eth_getBlockByNumber, eth_getPrice (custom)

## Integration Flow
```
Anvil RPC Fetch → Data Processing → Qwen Strategy Generation → BendVM Verification → Engine Execution → Results + Trace
```

## Quick Start
```bash
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