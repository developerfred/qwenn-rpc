"""Example: Data ingestion pipeline for neural-symbolic finance.

This example demonstrates the full pipeline:
1. Fetch market data from Anvil RPC
2. Process into BendLite format  
3. Generate BendLite strategy program using Qwen
4. Verify static rules
5. Execute and generate trace
"""

from qwenn_rpc.anvil_client import AnvilRPCClient, fetch_block_data
from qwenn_rpc.market_data import (
    get_market_data_from_anvil,
    format_market_data_for_bend,
    price_to_u32,
    pipeline_price_momentum,
)
from qwenn_strategies.strategy_gen import generate_strategy, verify_strategy, execute_strategy


def main() -> None:
    """Run the full data ingestion and strategy generation pipeline."""
    
    # Step 1: Connect to Anvil and fetch data
    print("=" * 60)
    print("Qwenn-RPC: Data Ingestion Pipeline")
    print("=" * 60)
    print()
    
    # Connect to local Anvil
    rpc_url = "http://127.0.0.1:8545"
    client = AnvilRPCClient(rpc_url)
    
    if not client.health_check():
        print("❌ Anvil RPC not healthy! Start Anvil first.")
        print("   Example: anvil --chain sepolia")
        return
    
    print("✅ Anvil RPC connection healthy")
    print()
    
    # Step 2: Fetch market data
    print("📡 Fetching market data from Anvil...")
    raw_data = get_market_data_from_anvil(rpc_url=rpc_url)
    
    eth_price = raw_data["eth_price_usd"]
    print(f"   ETH/USD Price: ${eth_price or 'Using fallback'}")
    print(f"   Block number: {raw_data['block_number']}")
    print(f"   Timestamp: {raw_data['timestamp']}")
    print()
    
    # Step 3: Format for BendLite
    bend_data = format_market_data_for_bend(
        block_number=raw_data["block_number"],
        timestamp=raw_data["timestamp"],
        eth_price_usd=eth_price,
    )
    
    print("📐 BendLite-formatted market data:")
    for key, value in bend_data.items():
        print(f"   {key}: {value}")
    print()
    
    # Step 4: Calculate momentum indicators
    print("⚡ Calculating price momentum...")
    # Example price series (in real use, get from historical data)
    price_series_usd = [3000.0, 3050.0, 3020.0, 3100.0, 3150.0, 3120.0, 3200.0]
    price_series_u32 = format_price_series_for_rsi(price_series_usd)
    
    if len(price_series_u32) >= 2:
        current_u32, prev_u32, direction = pipeline_price_momentum(
            price_series_u32[-1], price_series_u32[-2]
        )
        print(f"   Current price U32: {current_u32}")
        print(f"   Previous price U32: {prev_u32}")
        print(f"   Momentum direction: {direction}")
    print()
    
    # Step 5: Generate BendLite strategy program
    print("🧠 Generating BendLite strategy program with Qwen...")
    
    # Create market data description for the prompt
    market_desc = f"""
    Market data:
    - ETH price: ${eth_price or 3000:.2f}
    - Block: {raw_data['block_number']}
    - Timestamp: {raw_data['timestamp']}
    - Momentum: {direction} (based on recent price series)
    - Prices: {price_series_usd}
    """
    
    strategy_program = generate_strategy(
        market_data=market_desc,
        strategy_type="rsi",
        parameters={"period": 14, "overbought": 70, "oversold": 30},
    )
    
    print("   Generated BendLite strategy (RSI):")
    print("   " + "\\n".join(strategy_program.split("\\n")[:10]))  # Show first 10 lines
    print("   ...")
    print()
    
    # Step 6: Verify static rules
    print("✅ Verifying Bend2 static rules...")
    verification = verify_strategy(strategy_program)
    print(f"   Valid: {verification['valid']}")
    print(f"   Type check: {verification['type_check']}")
    print(f"   Affine check: {verification['affine_check']}")
    print(f"   Termination check: {verification['termination_check']}")
    if verification["errors"]:
        print(f"   Errors: {verification['errors'][:3]}")  # Show first 3
    print()
    
    # Step 7: Execute and generate trace
    print("🏃 Executing strategy and generating trace...")
    execution = execute_strategy(strategy_program, ",".join(str(int(p)) for p in price_series_usd[:7]))
    
    print(f"   Success: {execution['success']}")
    print(f"   Compliance: {execution['compliance']}")
    print(f"   Result (U32): {execution['result']}")
    if execution["trace"]:
        print(f"   Trace tokens: {len(execution['trace'])}")
    print()
    
    # Step 8: Summary
    print("=" * 60)
    print("Pipeline Complete! Summary:")
    print("=" * 60)
    print(f"  • Market data fetched from Anvil RPC: ✅")
    print(f"  • BendLite format generated: ✅")
    print(f"  • Qwen-generated strategy: ✅")
    print(f"  • Static rules verification: {'✅' if verification['valid'] else '❌'}")
    print(f"  • Engine execution: {'✅' if execution['success'] else '❌'}")
    print(f"  • Trace generated: {len(execution['trace']) if execution['trace'] else 0} tokens")
    print()
    print("📋 Next steps:")
    print("  1. Review the generated strategy program")
    print("  2. Analyze the execution trace for debugging")
    print("  3. Backtest with historical data")
    print("  4. Integrate with real oracle price feeds")


if __name__ == "__main__":
    main()