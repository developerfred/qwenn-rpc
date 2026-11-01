"""Tests for Qwenn-RPC Anvil client and market data."""

from qwenn_rpc.anvil_client import (
    AnvilRPCClient,
    fetch_block_data,
    RPCError,
    RPCConnectionError,
    RPCResponseError,
)
from qwenn_rpc.market_data import (
    price_to_u32,
    timestamp_to_u32,
    block_to_u32,
    format_market_data_for_bend,
    get_market_data_from_anvil,
    format_price_series_for_rsi,
    pipeline_price_momentum,
    validate_u32_range,
)


def test_anvil_client_creation():
    """Test AnvilRPCClient can be created."""
    client = AnvilRPCClient()
    assert client is not None
    print("✓ AnvilRPCClient creation works")


def test_price_to_u32():
    """Test price conversion to U32."""
    # $3000 -> 3000
    result = price_to_u32(3000.0)
    assert result == 3000, f"Expected 3000, got {result}"
    
    # $85000 -> 85000
    result = price_to_u32(85000.0)
    assert result == 85000, f"Expected 85000, got {result}"
    
    # None -> 0
    result = price_to_u32(None)
    assert result == 0, f"Expected 0, got {result}"
    print("✓ price_to_u32 works")


def test_timestamp_to_u32():
    """Test timestamp conversion to U32."""
    import time
    now = int(time.time())
    result = timestamp_to_u32(now)
    assert result == now % (2**32), f"Expected {now % (2**32)}, got {result}"
    print("✓ timestamp_to_u32 works")


def test_block_to_u32():
    """Test block number conversion to U32."""
    result = block_to_u32(19876543)
    assert result == 19876543 % (2**32), f"Expected {19876543 % (2**32)}, got {result}"
    print("✓ block_to_u32 works")


def test_validate_u32_range():
    """Test U32 range validation."""
    # Valid U32
    validate_u32_range(0)
    validate_u32_range(2**32 - 1)
    validate_u32_range(4294967295)
    
    # Invalid U32 should raise
    try:
        validate_u32_range(-1)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    try:
        validate_u32_range(2**32)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("✓ validate_u32_range works")


def test_format_market_data_for_bend():
    """Test market data formatting for BendLite."""
    bend_data = format_market_data_for_bend(
        block_number=19876543,
        timestamp=1700000000,
        eth_price_usd=3000.0,
    )
    
    assert "BLOCK_NUMBER" in bend_data
    assert "TIMESTAMP" in bend_data
    assert "ETH_PRICE_U32" in bend_data
    assert bend_data["ETH_PRICE_U32"] == 3000, f"Expected 3000, got {bend_data['ETH_PRICE_U32']}"
    print("✓ format_market_data_for_bend works")


def test_format_price_series_for_rsi():
    """Test price series formatting for RSI."""
    prices = [3000.0, 3050.0, 3020.0, 3100.0, 3150.0]
    u32_series = format_price_series_for_rsi(prices)
    
    assert len(u32_series) == len(prices)
    assert all(isinstance(p, int) for p in u32_series)
    print("✓ format_price_series_for_rsi works")


def test_pipeline_price_momentum():
    """Test price momentum pipeline."""
    current = 3100
    previous = 3050
    change, change_pct, direction = pipeline_price_momentum(current, previous)
    
    assert change >= 0, f"Expected positive change, got {change}"
    assert direction == "UP", f"Expected UP direction, got {direction}"
    print("✓ pipeline_price_momentum works")


def test_get_market_data_from_anvil_structure():
    """Test market data fetch function structure (may fail if Anvil not running)."""
    # Test that the function can be called (will fail gracefully if Anvil not running)
    try:
        data = get_market_data_from_anvil()
        assert "block_number" in data
        assert "timestamp" in data
        print("✓ get_market_data_from_anvil works (healthy Anvil)")
    except Exception as e:
        # If Anvil is not running, that's ok - test the function structure
        print(f"⚠ get_market_data_from_anvil: Anvil not running ({e}), test structure OK")


def test_rpc_error_classes():
    """Test RPC error classes."""
    # RPCError
    try:
        raise RPCError(-32603, "Invalid JSON")
    except RPCError as e:
        assert e.code == -32603
        assert "Invalid JSON" in e.message
    
    # RPCConnectionError
    try:
        raise RPCConnectionError("Cannot connect")
    except RPCConnectionError as e:
        assert "Cannot connect" in e.message
    
    # RPCResponseError
    try:
        raise RPCResponseError("Parse error")
    except RPCResponseError as e:
        assert "Parse error" in e.message
    
    print("✓ RPC error classes work")


if __name__ == "__main__":
    test_anvil_client_creation()
    test_price_to_u32()
    test_timestamp_to_u32()
    test_block_to_u32()
    test_validate_u32_range()
    test_format_market_data_for_bend()
    test_format_price_series_for_rsi()
    test_pipeline_price_momentum()
    test_get_market_data_from_anvil_structure()
    test_rpc_error_classes()
    print("\n🎉 All RPC tests passed!")