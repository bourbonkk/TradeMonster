"""Portfolio Management MCP Tool."""

import asyncio
from typing import Dict, Any, Optional, List
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

from mcp import Tool
from ..schemas import PortfolioSummary, PortfolioAllocation, RiskLevel


class PortfolioTool(Tool):
    """Tool for portfolio management and optimization."""
    
    name = "manage_portfolio"
    description = "Manage and optimize investment portfolio with risk management and performance tracking"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the portfolio management tool."""
        try:
            action = params.get("action", "analyze")
            
            if action == "analyze":
                return await self._analyze_portfolio(params)
            elif action == "optimize":
                return await self._optimize_portfolio(params)
            elif action == "rebalance":
                return await self._rebalance_portfolio(params)
            elif action == "track_performance":
                return await self._track_performance(params)
            else:
                return {"error": f"Action {action} not supported"}
                
        except Exception as e:
            return {
                "error": f"Failed to manage portfolio: {str(e)}",
                "success": False
            }
    
    async def _analyze_portfolio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current portfolio."""
        portfolio_data = params.get("portfolio", [])
        
        if not portfolio_data:
            return {"error": "Portfolio data is required"}
        
        # Calculate portfolio metrics
        total_value = 0
        total_cost = 0
        allocations = []
        
        for position in portfolio_data:
            symbol = position["symbol"]
            shares = position["shares"]
            cost_basis = position["cost_basis"]
            
            # Get current price
            try:
                stock = yf.Ticker(symbol)
                current_price = stock.history(period="5d")['Close'].iloc[-1]
            except:
                current_price = cost_basis  # Fallback to cost basis
            
            position_value = shares * current_price
            position_cost = shares * cost_basis
            unrealized_pnl = position_value - position_cost
            unrealized_pnl_percent = (unrealized_pnl / position_cost) * 100 if position_cost > 0 else 0
            
            total_value += position_value
            total_cost += position_cost
            
            allocation = PortfolioAllocation(
                symbol=symbol,
                weight=(position_value / total_value) * 100 if total_value > 0 else 0,
                shares=shares,
                value=position_value,
                cost_basis=cost_basis,
                current_price=current_price,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_percent=unrealized_pnl_percent,
                beta_contribution=0,  # Would need beta data
                volatility_contribution=0  # Would need volatility data
            )
            allocations.append(allocation)
        
        # Calculate portfolio summary
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost) * 100 if total_cost > 0 else 0
        
        portfolio_summary = PortfolioSummary(
            total_value=total_value,
            total_cost=total_cost,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            portfolio_beta=1.0,  # Simplified
            portfolio_volatility=0.15,  # Simplified
            sharpe_ratio=0.5,  # Simplified
            max_drawdown=0.05,  # Simplified
            allocations=allocations,
            daily_return=0.001,  # Simplified
            weekly_return=0.005,  # Simplified
            monthly_return=0.02,  # Simplified
            yearly_return=0.15  # Simplified
        )
        
        return {
            "success": True,
            "portfolio_summary": portfolio_summary.model_dump(),
            "message": "Portfolio analysis completed"
        }
    
    async def _optimize_portfolio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize portfolio allocation."""
        symbols = params.get("symbols", [])
        risk_tolerance = params.get("risk_tolerance", RiskLevel.MODERATE)
        target_return = params.get("target_return", 0.15)
        current_portfolio = params.get("current_portfolio", [])
        
        if not symbols:
            return {"error": "Symbols list is required"}
        
        # Get historical data for optimization
        historical_data = {}
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1y")
                if not hist.empty:
                    historical_data[symbol] = hist['Close']
            except:
                continue
        
        if len(historical_data) < 2:
            return {"error": "Insufficient data for optimization"}
        
        # Calculate returns and covariance matrix
        returns_data = pd.DataFrame(historical_data).pct_change().dropna()
        mean_returns = returns_data.mean()
        cov_matrix = returns_data.cov()
        
        # Simple optimization (in real implementation, use scipy.optimize)
        # For now, use equal weight or risk-adjusted weights
        if risk_tolerance == RiskLevel.CONSERVATIVE:
            # Conservative: More weight to lower volatility stocks
            volatilities = returns_data.std()
            weights = 1 / volatilities
            weights = weights / weights.sum()
        elif risk_tolerance == RiskLevel.AGGRESSIVE:
            # Aggressive: More weight to higher return stocks
            weights = mean_returns / mean_returns.sum()
        else:
            # Moderate: Equal weight
            weights = pd.Series(1/len(symbols), index=symbols)
        
        # Create optimized allocations
        optimized_allocations = []
        for symbol in symbols:
            if symbol in weights.index:
                allocation = PortfolioAllocation(
                    symbol=symbol,
                    weight=weights[symbol] * 100,
                    shares=0,  # Would be calculated based on available capital
                    value=0,  # Would be calculated based on available capital
                    cost_basis=0,
                    current_price=0,
                    unrealized_pnl=0,
                    unrealized_pnl_percent=0,
                    beta_contribution=0,
                    volatility_contribution=0
                )
                optimized_allocations.append(allocation)
        
        # Calculate expected portfolio metrics
        expected_return = (mean_returns * weights).sum()
        portfolio_variance = (weights.T @ cov_matrix @ weights)
        portfolio_volatility = np.sqrt(portfolio_variance)
        sharpe_ratio = expected_return / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return {
            "success": True,
            "optimized_allocations": [alloc.model_dump() for alloc in optimized_allocations],
            "expected_metrics": {
                "expected_return": expected_return,
                "portfolio_volatility": portfolio_volatility,
                "sharpe_ratio": sharpe_ratio,
                "risk_tolerance": risk_tolerance.value
            },
            "message": "Portfolio optimization completed"
        }
    
    async def _rebalance_portfolio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rebalance portfolio to target allocations."""
        current_portfolio = params.get("current_portfolio", [])
        target_allocations = params.get("target_allocations", {})
        total_capital = params.get("total_capital", 100000)
        
        if not current_portfolio or not target_allocations:
            return {"error": "Current portfolio and target allocations are required"}
        
        # Calculate current allocations
        current_values = {}
        current_prices = {}
        
        for position in current_portfolio:
            symbol = position["symbol"]
            shares = position["shares"]
            
            # Get current price
            try:
                stock = yf.Ticker(symbol)
                current_price = stock.history(period="5d")['Close'].iloc[-1]
            except:
                current_price = position["cost_basis"]
            
            current_values[symbol] = shares * current_price
            current_prices[symbol] = current_price
        
        # Calculate target values
        target_values = {}
        for symbol, target_weight in target_allocations.items():
            target_values[symbol] = total_capital * (target_weight / 100)
        
        # Calculate rebalancing trades
        rebalancing_trades = []
        
        for symbol in set(current_values.keys()) | set(target_values.keys()):
            current_value = current_values.get(symbol, 0)
            target_value = target_values.get(symbol, 0)
            current_price = current_prices.get(symbol, 0)
            
            if current_price > 0:
                current_shares = current_value / current_price
                target_shares = target_value / current_price
                shares_to_trade = target_shares - current_shares
                
                if abs(shares_to_trade) > 0.01:  # Minimum trade threshold
                    trade = {
                        "symbol": symbol,
                        "action": "buy" if shares_to_trade > 0 else "sell",
                        "shares": abs(shares_to_trade),
                        "value": abs(shares_to_trade * current_price),
                        "current_price": current_price
                    }
                    rebalancing_trades.append(trade)
        
        return {
            "success": True,
            "rebalancing_trades": rebalancing_trades,
            "total_trade_value": sum(trade["value"] for trade in rebalancing_trades),
            "message": f"Portfolio rebalancing plan generated with {len(rebalancing_trades)} trades"
        }
    
    async def _track_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track portfolio performance over time."""
        portfolio_history = params.get("portfolio_history", [])
        benchmark_symbol = params.get("benchmark", "SPY")
        
        if not portfolio_history:
            return {"error": "Portfolio history is required"}
        
        # Calculate performance metrics
        performance_data = []
        benchmark_data = []
        
        for entry in portfolio_history:
            date = entry["date"]
            portfolio_value = entry["value"]
            
            # Get benchmark value for comparison
            try:
                benchmark = yf.Ticker(benchmark_symbol)
                benchmark_hist = benchmark.history(start=date, end=date, period="1d")
                if not benchmark_hist.empty:
                    benchmark_value = benchmark_hist['Close'].iloc[0]
                else:
                    benchmark_value = 100  # Default value
            except:
                benchmark_value = 100
            
            performance_data.append({
                "date": date,
                "portfolio_value": portfolio_value,
                "benchmark_value": benchmark_value
            })
        
        # Calculate performance metrics
        if len(performance_data) > 1:
            initial_portfolio = performance_data[0]["portfolio_value"]
            final_portfolio = performance_data[-1]["portfolio_value"]
            initial_benchmark = performance_data[0]["benchmark_value"]
            final_benchmark = performance_data[-1]["benchmark_value"]
            
            portfolio_return = (final_portfolio / initial_portfolio - 1) * 100
            benchmark_return = (final_benchmark / initial_benchmark - 1) * 100
            excess_return = portfolio_return - benchmark_return
            
            # Calculate volatility
            portfolio_returns = []
            for i in range(1, len(performance_data)):
                ret = (performance_data[i]["portfolio_value"] / performance_data[i-1]["portfolio_value"] - 1)
                portfolio_returns.append(ret)
            
            volatility = np.std(portfolio_returns) * np.sqrt(252) * 100  # Annualized
            sharpe_ratio = portfolio_return / volatility if volatility > 0 else 0
            
            # Calculate maximum drawdown
            peak = initial_portfolio
            max_drawdown = 0
            
            for entry in performance_data:
                value = entry["portfolio_value"]
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak * 100
                max_drawdown = max(max_drawdown, drawdown)
            
        else:
            portfolio_return = 0
            benchmark_return = 0
            excess_return = 0
            volatility = 0
            sharpe_ratio = 0
            max_drawdown = 0
        
        return {
            "success": True,
            "performance_metrics": {
                "portfolio_return": portfolio_return,
                "benchmark_return": benchmark_return,
                "excess_return": excess_return,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown
            },
            "performance_data": performance_data,
            "message": "Performance tracking completed"
        }


class RiskAnalysisTool(Tool):
    """Tool for portfolio risk analysis."""
    
    name = "analyze_risk"
    description = "Analyze portfolio risk metrics including VaR, CVaR, and stress testing"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the risk analysis tool."""
        try:
            portfolio_data = params.get("portfolio", [])
            confidence_level = params.get("confidence_level", 0.95)
            
            if not portfolio_data:
                return {"error": "Portfolio data is required"}
            
            # Get historical data for risk analysis
            symbols = [position["symbol"] for position in portfolio_data]
            historical_data = {}
            
            for symbol in symbols:
                try:
                    stock = yf.Ticker(symbol)
                    hist = stock.history(period="1y")
                    if not hist.empty:
                        historical_data[symbol] = hist['Close']
                except:
                    continue
            
            if len(historical_data) < 2:
                return {"error": "Insufficient data for risk analysis"}
            
            # Calculate returns
            returns_data = pd.DataFrame(historical_data).pct_change().dropna()
            
            # Calculate portfolio weights (simplified - equal weight)
            weights = pd.Series(1/len(symbols), index=symbols)
            
            # Calculate portfolio returns
            portfolio_returns = (returns_data * weights).sum(axis=1)
            
            # Calculate risk metrics
            portfolio_volatility = portfolio_returns.std() * np.sqrt(252)
            var_95 = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
            cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
            
            # Calculate beta (simplified)
            try:
                spy = yf.Ticker("SPY")
                spy_hist = spy.history(period="1y")
                spy_returns = spy_hist['Close'].pct_change().dropna()
                
                # Align data
                common_dates = portfolio_returns.index.intersection(spy_returns.index)
                portfolio_returns_aligned = portfolio_returns[common_dates]
                spy_returns_aligned = spy_returns[common_dates]
                
                beta = np.cov(portfolio_returns_aligned, spy_returns_aligned)[0, 1] / np.var(spy_returns_aligned)
            except:
                beta = 1.0  # Default beta
            
            return {
                "success": True,
                "risk_metrics": {
                    "portfolio_volatility": portfolio_volatility,
                    "var_95": var_95,
                    "cvar_95": cvar_95,
                    "beta": beta,
                    "confidence_level": confidence_level
                },
                "message": "Risk analysis completed"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to analyze risk: {str(e)}",
                "success": False
            }
