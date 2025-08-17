"""Stock Information MCP Tool."""

import asyncio
from typing import Dict, Any, Optional, List
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

from mcp import Tool
from ..schemas import StockInfo


class StockInfoTool(Tool):
    """Tool for retrieving stock information and financial data."""
    
    name = "get_stock_info"
    description = "Get comprehensive stock information including price, financials, and company details"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the stock info tool."""
        try:
            symbol = params.get("symbol", "").upper()
            include_financials = params.get("include_financials", False)
            include_news = params.get("include_news", False)
            
            if not symbol:
                return {"error": "Symbol is required"}
            
            # Get stock info using yfinance
            stock = yf.Ticker(symbol)
            
            # Get basic info
            info = stock.info
            
            # Get current price data
            hist = stock.history(period="5d")
            if hist.empty:
                return {"error": f"No data found for symbol {symbol}"}
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100 if prev_price != 0 else 0
            
            # Build stock info
            stock_info = StockInfo(
                symbol=symbol,
                name=info.get('longName', info.get('shortName', symbol)),
                sector=info.get('sector'),
                industry=info.get('industry'),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                price=current_price,
                change=change,
                change_percent=change_percent,
                volume=hist['Volume'].iloc[-1],
                avg_volume=info.get('averageVolume'),
                high_52w=info.get('fiftyTwoWeekHigh'),
                low_52w=info.get('fiftyTwoWeekLow'),
                dividend_yield=info.get('dividendYield'),
                beta=info.get('beta')
            )
            
            result = {
                "success": True,
                "stock_info": stock_info.model_dump(),
                "message": f"Successfully retrieved information for {symbol}"
            }
            
            # Add financial data if requested
            if include_financials:
                financials = await self._get_financial_data(stock)
                result["financials"] = financials
            
            # Add news if requested
            if include_news:
                news = await self._get_news_data(stock)
                result["news"] = news
            
            return result
            
        except Exception as e:
            return {
                "error": f"Failed to get stock info: {str(e)}",
                "success": False
            }
    
    async def _get_financial_data(self, stock: yf.Ticker) -> Dict[str, Any]:
        """Get financial data for the stock."""
        try:
            # Get financial statements
            income_stmt = stock.income_stmt
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            financials = {
                "income_statement": {},
                "balance_sheet": {},
                "cash_flow": {}
            }
            
            if not income_stmt.empty:
                financials["income_statement"] = {
                    "revenue": income_stmt.loc['Total Revenue'].iloc[0] if 'Total Revenue' in income_stmt.index else None,
                    "net_income": income_stmt.loc['Net Income'].iloc[0] if 'Net Income' in income_stmt.index else None,
                    "eps": income_stmt.loc['Basic EPS'].iloc[0] if 'Basic EPS' in income_stmt.index else None,
                    "gross_margin": income_stmt.loc['Gross Profit'].iloc[0] if 'Gross Profit' in income_stmt.index else None
                }
            
            if not balance_sheet.empty:
                financials["balance_sheet"] = {
                    "total_assets": balance_sheet.loc['Total Assets'].iloc[0] if 'Total Assets' in balance_sheet.index else None,
                    "total_liabilities": balance_sheet.loc['Total Liabilities'].iloc[0] if 'Total Liabilities' in balance_sheet.index else None,
                    "total_equity": balance_sheet.loc['Total Equity'].iloc[0] if 'Total Equity' in balance_sheet.index else None,
                    "cash": balance_sheet.loc['Cash'].iloc[0] if 'Cash' in balance_sheet.index else None
                }
            
            if not cash_flow.empty:
                financials["cash_flow"] = {
                    "operating_cash_flow": cash_flow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cash_flow.index else None,
                    "investing_cash_flow": cash_flow.loc['Investing Cash Flow'].iloc[0] if 'Investing Cash Flow' in cash_flow.index else None,
                    "financing_cash_flow": cash_flow.loc['Financing Cash Flow'].iloc[0] if 'Financing Cash Flow' in cash_flow.index else None
                }
            
            return financials
            
        except Exception as e:
            return {"error": f"Failed to get financial data: {str(e)}"}
    
    async def _get_news_data(self, stock: yf.Ticker) -> List[Dict[str, Any]]:
        """Get recent news for the stock."""
        try:
            news = stock.news
            return [
                {
                    "title": article.get('title', ''),
                    "publisher": article.get('publisher', ''),
                    "link": article.get('link', ''),
                    "published": article.get('providerPublishTime', ''),
                    "summary": article.get('summary', '')
                }
                for article in news[:10]  # Limit to 10 most recent articles
            ]
        except Exception as e:
            return [{"error": f"Failed to get news: {str(e)}"}]


class MarketScreenerTool(Tool):
    """Tool for screening stocks based on various criteria."""
    
    name = "screen_stocks"
    description = "Screen stocks based on technical and fundamental criteria"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the stock screener tool."""
        try:
            # Get screening criteria
            min_market_cap = params.get("min_market_cap", 1000000000)  # 1B default
            max_pe_ratio = params.get("max_pe_ratio", 50)
            min_volume = params.get("min_volume", 1000000)  # 1M default
            sectors = params.get("sectors", [])
            technical_filters = params.get("technical_filters", {})
            
            # This is a simplified implementation
            # In a real implementation, you would query a database or use a screening API
            
            # For now, return a sample result
            sample_stocks = [
                {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "market_cap": 3000000000000, "pe_ratio": 25.5},
                {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "market_cap": 2800000000000, "pe_ratio": 30.2},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "market_cap": 1800000000000, "pe_ratio": 28.1},
            ]
            
            # Apply filters
            filtered_stocks = []
            for stock in sample_stocks:
                if (stock["market_cap"] >= min_market_cap and
                    stock["pe_ratio"] <= max_pe_ratio and
                    (not sectors or stock["sector"] in sectors)):
                    filtered_stocks.append(stock)
            
            return {
                "success": True,
                "stocks": filtered_stocks,
                "total_count": len(filtered_stocks),
                "criteria_used": {
                    "min_market_cap": min_market_cap,
                    "max_pe_ratio": max_pe_ratio,
                    "min_volume": min_volume,
                    "sectors": sectors
                }
            }
            
        except Exception as e:
            return {
                "error": f"Failed to screen stocks: {str(e)}",
                "success": False
            }
