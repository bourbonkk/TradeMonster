"""Trend Following MCP Server."""

import asyncio
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from mcp import Server, StdioServerParameters
from mcp.server.models import InitializationOptions

from .tools import (
    StockInfoTool,
    TechnicalAnalysisTool,
    TradingSignalTool,
    PortfolioTool
)
from .tools.stock_info import MarketScreenerTool
from .tools.signals import SignalBacktestTool
from .tools.portfolio import RiskAnalysisTool


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrendFollowingMCPServer:
    """Trend Following MCP Server implementation."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("trend-following-mcp")
        self.tools = [
            StockInfoTool(),
            MarketScreenerTool(),
            TechnicalAnalysisTool(),
            TradingSignalTool(),
            SignalBacktestTool(),
            PortfolioTool(),
            RiskAnalysisTool()
        ]
        
        # Register tools
        for tool in self.tools:
            self.server.register_tool(tool)
        
        # Register handlers
        self.server.on_initialize(self._on_initialize)
        self.server.on_shutdown(self._on_shutdown)
    
    async def _on_initialize(self, params: InitializationOptions) -> Dict[str, Any]:
        """Handle server initialization."""
        logger.info("Initializing Trend Following MCP Server")
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "trend-following-mcp",
                "version": "0.1.0"
            }
        }
    
    async def _on_shutdown(self) -> None:
        """Handle server shutdown."""
        logger.info("Shutting down Trend Following MCP Server")
    
    async def start(self, stdio: bool = True) -> None:
        """Start the MCP server."""
        if stdio:
            params = StdioServerParameters()
            await self.server.run(params)
        else:
            # For future WebSocket support
            logger.info("WebSocket support not implemented yet")


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Trend Following MCP Server")
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    parser.add_argument("--stdio", action="store_true", default=True, help="Use stdio transport")
    parser.add_argument("--port", type=int, default=8000, help="Port for WebSocket server")
    
    args = parser.parse_args()
    
    if args.dev:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Running in development mode")
    
    server = TrendFollowingMCPServer()
    
    try:
        await server.start(stdio=args.stdio)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
