#!/usr/bin/env python3
"""Script para buscar dados de mercado do Anvil RPC.

Usage:
    python fetch_data.py [--rpc URL] [--output FILE]
    
Options:
    --rpc URL           Anvil RPC endpoint (default: http://127.0.0.1:8545)
    --output FILE      Output JSON file path (default: market_data.json)
    --eth-price FLOAT   ETH price override (USD)
"""

import json
import argparse
from qwenn_rpc.market_data import get_market_data_from_anvil, format_market_data_for_bend


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch market data from Anvil RPC for QwenBend"
    )
    parser.add_argument(
        "--rpc",
        type=str,
        default="http://127.0.0.1:8545",
        help="Anvil RPC endpoint URL (default: http://127.0.0.1:8545)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="market_data.json",
        help="Output JSON file path (default: market_data.json)",
    )
    parser.add_argument(
        "--eth-price",
        type=float,
        default=None,
        help="ETH price override in USD (default: auto from Anvil or fallback)",
    )
    
    args = parser.parse_args()
    
    print(f"🔗 Connecting to Anvil RPC: {args.rpc}")
    print()
    
    # Fetch market data
    data = get_market_data_from_anvil(rpc_url=args.rpc, eth_price=args.eth_price)
    
    print(f"✅ Block number: {data['block_number']}")
    print(f"✅ Timestamp: {data['timestamp']}")
    print(f"✅ ETH price (USD): {data['eth_price_usd'] or 'Not available'}")
    print()
    
    # Format for BendLite
    bend_data = format_market_data_for_bend(
        block_number=data["block_number"],
        timestamp=data["timestamp"],
        eth_price_usd=data["eth_price_usd"],
    )
    
    print(f"📊 BendLite-formatted data:")
    for key, value in bend_data.items():
        print(f"  {key}: {value}")
    print()
    
    # Save to JSON file
    output_path = args.output
    with open(output_path, "w") as f:
        json.dump({**data, "bend_lite_format": bend_data}, f, indent=2)
    
    print(f"💾 Data saved to: {output_path}")
    print()
    print("🚀 Dados prontos para uso com QwenBend!")
    print("   Próximo passo: python -m qwenn_strategies generate rsi")


if __name__ == "__main__":
    main()