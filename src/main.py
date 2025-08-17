"""Main entry point for Trend Following MCP Server."""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import get_config
from utils.logger import setup_logger
from mcp.server import main as mcp_main


def main():
    """Main entry point."""
    # Setup configuration
    config = get_config()
    
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Trend Following MCP Server")
    logger.info(f"Version: {config.app_version}")
    logger.info(f"Environment: {config.is_development and 'Development' or 'Production'}")
    
    # Run MCP server
    try:
        asyncio.run(mcp_main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
