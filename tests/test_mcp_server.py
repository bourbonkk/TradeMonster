"""Tests for MCP Server."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.mcp.server import TrendFollowingMCPServer
from src.mcp.tools.stock_info import StockInfoTool
from src.mcp.tools.technical import TechnicalAnalysisTool
from src.mcp.tools.signals import TradingSignalTool
from src.mcp.tools.portfolio import PortfolioTool


class TestTrendFollowingMCPServer:
    """Test cases for TrendFollowingMCPServer."""
    
    @pytest.fixture
    def server(self):
        """Create server instance for testing."""
        return TrendFollowingMCPServer()
    
    def test_server_initialization(self, server):
        """Test server initialization."""
        assert server.server is not None
        assert len(server.tools) == 7  # All tools should be registered
        assert any(isinstance(tool, StockInfoTool) for tool in server.tools)
        assert any(isinstance(tool, TechnicalAnalysisTool) for tool in server.tools)
        assert any(isinstance(tool, TradingSignalTool) for tool in server.tools)
        assert any(isinstance(tool, PortfolioTool) for tool in server.tools)
    
    @pytest.mark.asyncio
    async def test_on_initialize(self, server):
        """Test server initialization handler."""
        params = Mock()
        result = await server._on_initialize(params)
        
        assert result["protocolVersion"] == "2024-11-05"
        assert result["serverInfo"]["name"] == "trend-following-mcp"
        assert result["serverInfo"]["version"] == "0.1.0"
    
    @pytest.mark.asyncio
    async def test_on_shutdown(self, server):
        """Test server shutdown handler."""
        # Should not raise any exceptions
        await server._on_shutdown()


class TestStockInfoTool:
    """Test cases for StockInfoTool."""
    
    @pytest.fixture
    def tool(self):
        """Create tool instance for testing."""
        return StockInfoTool()
    
    @pytest.mark.asyncio
    async def test_execute_missing_symbol(self, tool):
        """Test execution with missing symbol."""
        result = await tool.execute({})
        assert "error" in result
        assert "Symbol is required" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.mcp.tools.stock_info.yf.Ticker')
    async def test_execute_success(self, mock_ticker, tool):
        """Test successful execution."""
        # Mock yfinance response
        mock_stock = Mock()
        mock_stock.info = {
            'longName': 'Apple Inc.',
            'sector': 'Technology',
            'marketCap': 3000000000000,
            'trailingPE': 25.5,
            'averageVolume': 1000000,
            'fiftyTwoWeekHigh': 200.0,
            'fiftyTwoWeekLow': 150.0,
            'dividendYield': 0.02,
            'beta': 1.2
        }
        mock_stock.history.return_value = Mock()
        mock_stock.history.return_value.empty = False
        mock_stock.history.return_value.__getitem__.return_value.iloc = [100.0, 99.0]
        mock_ticker.return_value = mock_stock
        
        result = await tool.execute({"symbol": "AAPL"})
        
        assert result["success"] is True
        assert "stock_info" in result
        assert result["stock_info"]["symbol"] == "AAPL"
        assert result["stock_info"]["name"] == "Apple Inc."


class TestTechnicalAnalysisTool:
    """Test cases for TechnicalAnalysisTool."""
    
    @pytest.fixture
    def tool(self):
        """Create tool instance for testing."""
        return TechnicalAnalysisTool()
    
    @pytest.mark.asyncio
    async def test_execute_missing_symbol(self, tool):
        """Test execution with missing symbol."""
        result = await tool.execute({})
        assert "error" in result
        assert "Symbol is required" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.mcp.tools.technical.yf.Ticker')
    async def test_execute_success(self, mock_ticker, tool):
        """Test successful execution."""
        # Mock yfinance response
        mock_stock = Mock()
        mock_stock.history.return_value = Mock()
        mock_stock.history.return_value.empty = False
        mock_stock.history.return_value.__getitem__.return_value = Mock()
        mock_stock.history.return_value.__getitem__.return_value.iloc = [100.0]
        mock_stock.history.return_value.__getitem__.return_value.rolling.return_value.mean.return_value.iloc = [95.0, 90.0, 85.0]
        mock_stock.history.return_value.__getitem__.return_value.ewm.return_value.mean.return_value.iloc = [95.0, 90.0]
        mock_ticker.return_value = mock_stock
        
        result = await tool.execute({"symbol": "AAPL"})
        
        assert result["success"] is True
        assert "technical_indicators" in result
        assert result["technical_indicators"]["symbol"] == "AAPL"


class TestTradingSignalTool:
    """Test cases for TradingSignalTool."""
    
    @pytest.fixture
    def tool(self):
        """Create tool instance for testing."""
        return TradingSignalTool()
    
    @pytest.mark.asyncio
    async def test_execute_missing_symbol(self, tool):
        """Test execution with missing symbol."""
        result = await tool.execute({})
        assert "error" in result
        assert "Symbol is required" in result["error"]
    
    @pytest.mark.asyncio
    @patch('src.mcp.tools.signals.yf.Ticker')
    async def test_execute_success(self, mock_ticker, tool):
        """Test successful execution."""
        # Mock yfinance response
        mock_stock = Mock()
        mock_stock.history.return_value = Mock()
        mock_stock.history.return_value.empty = False
        mock_stock.history.return_value.__getitem__.return_value = Mock()
        mock_stock.history.return_value.__getitem__.return_value.iloc = [100.0]
        mock_stock.history.return_value.__getitem__.return_value.rolling.return_value.mean.return_value.iloc = [95.0, 90.0, 85.0]
        mock_stock.history.return_value.__getitem__.return_value.ewm.return_value.mean.return_value.iloc = [95.0, 90.0]
        mock_ticker.return_value = mock_stock
        
        result = await tool.execute({"symbol": "AAPL"})
        
        assert result["success"] is True
        assert "signal" in result
        assert result["signal"]["symbol"] == "AAPL"


class TestPortfolioTool:
    """Test cases for PortfolioTool."""
    
    @pytest.fixture
    def tool(self):
        """Create tool instance for testing."""
        return PortfolioTool()
    
    @pytest.mark.asyncio
    async def test_analyze_portfolio_missing_data(self, tool):
        """Test portfolio analysis with missing data."""
        result = await tool._analyze_portfolio({"portfolio": []})
        assert "error" in result
        assert "Portfolio data is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_analyze_portfolio_success(self, tool):
        """Test successful portfolio analysis."""
        portfolio_data = [
            {
                "symbol": "AAPL",
                "shares": 100,
                "cost_basis": 150.0
            }
        ]
        
        with patch('src.mcp.tools.portfolio.yf.Ticker') as mock_ticker:
            mock_stock = Mock()
            mock_stock.history.return_value = Mock()
            mock_stock.history.return_value.empty = False
            mock_stock.history.return_value.__getitem__.return_value.iloc = [160.0]
            mock_ticker.return_value = mock_stock
            
            result = await tool._analyze_portfolio({"portfolio": portfolio_data})
            
            assert result["success"] is True
            assert "portfolio_summary" in result
            assert result["portfolio_summary"]["total_value"] > 0


if __name__ == "__main__":
    pytest.main([__file__])
