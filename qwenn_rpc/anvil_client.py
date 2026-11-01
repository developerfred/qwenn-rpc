"""Anvil RPC client for fetching market data.

This module provides a client for connecting to Anvil (or any Ethereum-compatible
RPC endpoint) to fetch market data needed for neural-symbolic finance applications.

Supported data:
- Block number and timestamp
- ETH/USD price (via various oracles or direct price feeds)
- Account balances
- Transaction data
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional, Tuple

import requests


# Default Anvil RPC endpoint
DEFAULT_RPC_URL = "http://127.0.0.1:8545"

# RPC Methods
ETH_BLOCK_NUMBER = "eth_blockNumber"
GET_BLOCK_BY_NUMBER = "eth_getBlockByNumber"
GET_BLOCK_WITH_TXS = "eth_getBlockByNumber"  # with full txs if needed


class AnvilRPCClient:
    """Client for Anvil/Ethereum JSON-RPC communication."""
    
    def __init__(self, rpc_url: str = DEFAULT_RPC_URL):
        self.rpc_url = rpc_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
        })
    
    def _make_request(self, method: str, params: list = None) -> Dict[str, Any]:
        """Make a JSON-RPC request to the Anvil endpoint."""
        if params is None:
            params = []
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": int(time.time()),
        }
        
        try:
            response = self.session.post(self.rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Check for RPC errors
            if "error" in result:
                raise RPCError(
                    result["error"]["code"],
                    result["error"]["message"],
                )
            
            return result.get("result", {})
        
        except requests.exceptions.RequestException as e:
            raise RPCConnectionError(f"Failed to connect to RPC at {self.rpc_url}: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise RPCResponseError(f"Invalid RPC response: {e}")
    
    def fetch_block_number(self) -> int:
        """Fetch the latest block number."""
        result = self._make_request(ETH_BLOCK_NUMBER)
        return int(result, 16) if isinstance(result, str) else int(result)
    
    def fetch_block_by_number(self, block_number: str = "latest", full_transactions: bool = False) -> Dict[str, Any]:
        """Fetch block data by number.
        
        Args:
            block_number: Block number or "latest", "earliest", "pending"
            full_transactions: Whether to include full transaction objects
            
        Returns:
            Dict with block data including timestamp, difficulty, etc.
        """
        params = [block_number, "0x" if not full_transactions else True]
        result = self._make_request(GET_BLOCK_BY_NUMBER, params)
        
        # Convert hex values to int/str as needed
        if isinstance(result, dict):
            result["number"] = int(result.get("number", 0), 16) if result.get("number") else 0
            result["timestamp"] = int(result.get("timestamp", 0), 16) if result.get("timestamp") else 0
            result["difficulty"] = int(result.get("difficulty", 0), 16) if result.get("difficulty") else 0
            result["gas_limit"] = int(result.get("gasLimit", 0), 16) if result.get("gasLimit") else 0
            result["gas_used"] = int(result.get("gasUsed", 0), 16) if result.get("gasUsed") else 0
        
        return result
    
    def fetch_eth_price(self) -> Optional[float]:
        """Fetch ETH/USD price.
        
        Note: Anvil may not have direct price feeds. This method tries common approaches:
        - Check for custom Anvil price APIs
        - Return None if not available, caller should use external oracle
        
        Returns:
            ETH price in USD, or None if not available
        """
        # Anvil doesn't typically have built-in price feeds
        # This is a placeholder - in production, use Chainlink, CoinGecko, etc.
        try:
            # Try to check if Anvil has custom methods
            result = self._make_request("debug_getChainInfo")
            # Some Anvil setups may have price info in chain info
            price_str = result.get("ethUsdPrice")
            if price_str:
                return float(price_str)
        except Exception:
            pass
        
        # Return None - caller should use external oracle
        return None
    
    def fetch_account_balance(self, address: str) -> int:
        """Fetch ETH balance for an address (in wei)."""
        result = self._make_request("eth_getBalance", [address, "latest"])
        return int(result, 16) if result else 0
    
    def fetch_latest_block_data(self) -> Dict[str, Any]:
        """Fetch complete latest block data including timestamp and block number."""
        block_number = self.fetch_block_number()
        block_data = self.fetch_block_by_number(str(block_number))
        
        return {
            "block_number": block_number,
            "timestamp": block_data.get("timestamp", 0),
            "difficulty": block_data.get("difficulty", 0),
            "gas_limit": block_data.get("gas_limit", 0),
            "gas_used": block_data.get("gas_used", 0),
            "miner": block_data.get("miner", "unknown"),
        }
    
    def health_check(self) -> bool:
        """Check if the RPC endpoint is healthy and responsive."""
        try:
            self.fetch_block_number()
            return True
        except Exception:
            return False


class RPCError(Exception):
    """RPC-level error (error in the returned result)."""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"RPC Error {code}: {message}")


class RPCConnectionError(Exception):
    """Connection-level error (cannot reach the RPC endpoint)."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class RPCResponseError(Exception):
    """RPC response parsing error."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# Convenience function for quick data fetching
def fetch_block_data(rpc_url: str = DEFAULT_RPC_URL) -> Dict[str, Any]:
    """Quick function to fetch latest block data.
    
    Args:
        rpc_url: Anvil RPC endpoint URL
        
    Returns:
        Dict with block number, timestamp, and ETH price (price may be None)
    """
    client = AnvilRPCClient(rpc_url)
    block_number = client.fetch_block_number()
    block_info = client.fetch_latest_block_data()
    
    # Try to get ETH price (may be None)
    eth_price = client.fetch_eth_price()
    
    return {
        "block": block_number,
        "timestamp": block_info["timestamp"],
        "eth_price_usd": eth_price,
        "is_healthy": client.health_check(),
    }


# Example usage when run as script
if __name__ == "__main__":
    import sys
    
    rpc_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RPC_URL
    
    print(f"Connecting to Anvil RPC at {rpc_url}...")
    client = AnvilRPCClient(rpc_url)
    
    if not client.health_check():
        print("❌ RPC endpoint not healthy!")
        sys.exit(1)
    
    print("✅ RPC endpoint is healthy!")
    print()
    
    # Fetch and display block data
    block_number = client.fetch_block_number()
    block_info = client.fetch_latest_block_data()
    
    print(f"Latest Block Number: {block_number}")
    print(f"Timestamp: {block_info['timestamp']} ({(block_info['timestamp'] / 1000):.0f} ago if Unix)")
    print(f"Gas Limit: {block_info['gas_limit']:,}")
    print(f"Gas Used: {block_info['gas_used']:,}")
    
    # Try to get ETH price
    eth_price = client.fetch_eth_price()
    if eth_price:
        print(f"ETH/USD Price: ${eth_price:,.2f}")
    else:
        print("ETH/USD Price: Not available (use external oracle)")
        print("💡 Tip: Set up Chainlink or CoinGecko price feed")