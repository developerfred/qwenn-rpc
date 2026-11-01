"""Market data processing for Qwenn-RPC.

This module processes raw RPC data from Anvil/Ethereum into formats
compatible with BendLite and QwenBend neural-symbolic finance applications.

BendLite data format expectations:
- Prices: U32 (32-bit unsigned, mod 2^32)
- Timestamps: integer (Unix time in seconds or milliseconds)
- Block numbers: integer
- Quantities: U32
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union

from .anvil_client import (
    AnvilRPCClient,
    RPCError,
    RPCConnectionError,
    RPCResponseError,
    fetch_block_data,
)


# Type aliases for BendLite compatibility
U32 = int  # 32-bit unsigned integer (mod 2^32)
Nat = int  # Natural number


# ⚠️ IMPORTANTE: Anvil não tem feeds de preço integrados.
# Preços devem vir de oráculos externos (Chainlink, CoinGecko, etc.)
# Este módulo foca em dados de bloco que SÃO compatíveis com BendLite.

# Conversão: preço de mercado em USD -> U32 (mod 2^32)
# Para criptomoedas como ETH a ~$3000, usamos o valor inteiro 3000
# Para BTC a ~$85000, usamos 85000
# O wrap-around U32 (2^32 = 4294967296) é tratado automaticamente

# Fatores de conversão comuns
SATOSHI_TO_BTC = 100_000_000  # 1 BTC = 100M satoshis
WEI_TO_ETH = 10**18  # 1 ETH = 10^18 wei


def price_to_u32(price_usd: float) -> U32:
    """Convert price in USD to U32 format.
    
    Args:
        price_usd: Price in US dollars (float)
        
    Returns:
        U32 price value (integer, mod 2^32)
        
    Example:
        >>> price_to_u32(3000.0)
        3000
    """
    if price_usd is None:
        return 0
    # Converter para inteiro, garantindo bounds U32
    price_int = int(price_usd)
    return price_int % (2**32)


def timestamp_to_u32(timestamp: int) -> U32:
    """Convert Unix timestamp to U32 format.
    
    Args:
        timestamp: Unix timestamp in seconds
        
    Returns:
        U32 timestamp value
    """
    return timestamp % (2**32)


def block_to_u32(block_number: int) -> U32:
    """Convert block number to U32 format."""
    return block_number % (2**32)


def format_market_data_for_bend(
    block_number: int,
    timestamp: int, 
    eth_price_usd: Optional[float],
    eth_price_fallback: float = 3000.0
) -> Dict[str, U32]:
    """Format market data into BendLite-compatible U32 dict.
    
    Args:
        block_number: Latest block number
        timestamp: Unix timestamp in seconds  
        eth_price_usd: ETH price in USD (if None, uses fallback)
        eth_price_fallback: Fallback price if external price not available
        
    Returns:
        Dict with U32 values compatible with BendLite
    """
    # Use fallback price if none provided
    price = eth_price_usd if eth_price_usd is not None else eth_price_fallback
    
    return {
        "BLOCK_NUMBER": block_to_u32(block_number),
        "TIMESTAMP": timestamp_to_u32(timestamp),
        "ETH_PRICE_U32": price_to_u32(price),
        # Additional market data can be added here
        "OPEN_PRICE": price_to_u32(price),  # Simplified: open = current
        "HIGH_PRICE": price_to_u32(price * 1.05),  # 5% higher
        "LOW_PRICE": price_to_u32(price * 0.95),  # 5% lower
    }


def get_market_data_from_anvil(
    rpc_url: str = "http://127.0.0.1:8545",
    eth_price: Optional[float] = None,
) -> Dict[str, Union[int, float, None]]:
    """Fetch and process market data from Anvil RPC.
    
    Args:
        rpc_url: Anvil RPC endpoint
        eth_price: Optional ETH price override (uses external oracle if None)
        
    Returns:
        Dict with raw and processed market data
    """
    client = AnvilRPCClient(rpc_url)
    
    # Fetch block data
    block_data = client.fetch_latest_block_data()
    block_number = client.fetch_block_number()
    
    # Fetch ETH price
    price = client.fetch_eth_price()
    if price is None and eth_price:
        price = eth_price  # Use provided price
    
    # Format for BendLite
    bend_data = format_market_data_for_bend(
        block_number=block_number,
        timestamp=block_data["timestamp"],
        eth_price_usd=price,
    )
    
    return {
        "block_number": block_number,
        "timestamp": block_data["timestamp"],
        "eth_price_usd": price,
        "bend_lite_format": bend_data,
        "is_healthy": client.health_check(),
    }


# Example data processing pipelines
def pipeline_price_momentum(
    current_price: U32,
    previous_price: U32,
) -> Tuple[U32, U32, str]:
    """Calculate price momentum indicators.
    
    Returns:
        Tuple of (price_change, price_change_pct, direction)
        direction: "UP", "DOWN", or "NEUTRAL"
    """
    # price_change = current - previous (U32 arithmetic)
    # Handle wrap-around: if current < previous, price wrapped past 2^32
    if current_price >= previous_price:
        price_change = current_price - previous_price
    else:
        # Wrap-around case: price went from near 2^32 to 0
        price_change = (2**32 - previous_price) + current_price
    
    # Calculate percentage change (in basis points * 100 for U32 precision)
    if previous_price > 0:
        # Use float for percentage calc, then convert back
        price_change_pct = (price_change / previous_price) * 10000  # in bps
        price_change_pct_u32 = int(price_change_pct) % (2**32)
    else:
        price_change_pct_u32 = 0
    
    # Determine direction
    if price_change > 0:
        direction = "UP"
    elif price_change < 2**31:  # More than half of U32 range down
        direction = "DOWN"
    else:
        direction = "NEUTRAL"
    
    return price_change, price_change_pct_u32, direction


def format_price_series_for_rsi(
    prices: List[float],
    u32_conversion: bool = True,
) -> List[U32]:
    """Convert price series to U32 list for RSI calculation.
    
    Args:
        prices: List of price floats
        u32_conversion: Whether to convert to U32 format
        
    Returns:
        List of U32 price values
    """
    if u32_conversion:
        return [price_to_u32(p) for p in prices]
    else:
        # Return as-is (caller must ensure they're already U32)
        return [int(p) for p in prices]


# Validation and utilities
def validate_u32_range(value: int, name: str = "value") -> None:
    """Validate that a value is within U32 range [0, 2^32-1].
    
    Args:
        value: Value to validate
        name: Name for error messages
        
    Raises:
        ValueError: If value is outside U32 range
    """
    if not isinstance(value, int):
        raise ValueError(f"{name} must be integer, got {type(value)}")
    if value < 0 or value >= 2**32:
        raise ValueError(f"{name} must be in range [0, 2^32-1], got {value}")


# Legacy compatibility: old function names
fetch_block_data = fetch_block_data  # alias maintained for backward compat


# When run as module, show available functions
if __name__ == "__main__":
    print("Qwenn-RPC Market Data Processing Module")
    print("=" * 50)
    print("Available functions:")
    print("  - price_to_u32(): Convert USD price to U32")
    print("  - timestamp_to_u32(): Convert timestamp to U32")
    print("  - format_market_data_for_bend(): Format for BendLite")
    print("  - get_market_data_from_anvil(): Fetch from Anvil RPC")
    print("  - pipeline_price_momentum(): Calculate momentum")
    print("  - format_price_series_for_rsi(): Format prices for RSI")
    print("  - validate_u32_range(): Validate U32 range")
    print()
    print("Example:")
    print("  from qwenn_rpc.market_data import price_to_u32, get_market_data_from_anvil")
    print("  price = price_to_u32(3000.50)")
    print("  data = get_market_data_from_anvil()")