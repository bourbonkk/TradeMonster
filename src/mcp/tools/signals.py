"""Trading Signals MCP Tool."""

import asyncio
from typing import Dict, Any, Optional, List
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

from mcp import Tool
from ..schemas import TradingSignal, SignalType, RiskLevel


class TradingSignalTool(Tool):
    """Tool for generating trading signals based on trend following strategy."""
    
    name = "generate_signal"
    description = "Generate trading signals based on trend following analysis and risk management"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the trading signal tool."""
        try:
            symbol = params.get("symbol", "").upper()
            strategy = params.get("strategy", "trend_following")
            risk_level = params.get("risk_level", RiskLevel.MODERATE)
            position_size = params.get("position_size", 0.1)  # 10% default
            
            if not symbol:
                return {"error": "Symbol is required"}
            
            # Get stock data and technical analysis
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")
            
            if hist.empty:
                return {"error": f"No data found for symbol {symbol}"}
            
            # Get current price
            current_price = hist['Close'].iloc[-1]
            
            # Perform technical analysis
            technical_analysis = await self._perform_technical_analysis(hist)
            
            # Generate signal based on strategy
            if strategy == "trend_following":
                signal = await self._generate_trend_following_signal(
                    symbol, current_price, technical_analysis, risk_level
                )
            else:
                return {"error": f"Strategy {strategy} not implemented"}
            
            # Calculate position sizing and risk management
            signal = await self._add_risk_management(signal, current_price, technical_analysis, risk_level, position_size)
            
            return {
                "success": True,
                "signal": signal.model_dump(),
                "analysis": technical_analysis,
                "message": f"Trading signal generated for {symbol}"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate trading signal: {str(e)}",
                "success": False
            }
    
    async def _perform_technical_analysis(self, hist: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive technical analysis."""
        current_price = hist['Close'].iloc[-1]
        
        # Calculate moving averages
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        sma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        
        # Calculate RSI
        rsi = self._calculate_rsi(hist['Close'])
        
        # Calculate MACD
        macd_data = self._calculate_macd(hist['Close'])
        
        # Calculate Bollinger Bands
        bb_data = self._calculate_bollinger_bands(hist['Close'])
        
        # Calculate ATR for volatility
        atr = self._calculate_atr(hist)
        
        # Determine trend
        trend_direction = "up" if current_price > sma_50 > sma_200 else "down" if current_price < sma_50 < sma_200 else "sideways"
        
        return {
            "current_price": current_price,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi": rsi,
            "macd": macd_data,
            "bollinger_bands": bb_data,
            "atr": atr,
            "trend_direction": trend_direction,
            "price_position": (current_price - bb_data["lower"]) / (bb_data["upper"] - bb_data["lower"])
        }
    
    async def _generate_trend_following_signal(
        self, 
        symbol: str, 
        current_price: float, 
        analysis: Dict[str, Any], 
        risk_level: RiskLevel
    ) -> TradingSignal:
        """Generate trend following trading signal."""
        
        # Initialize signal components
        signal_type = SignalType.HOLD
        confidence = 50.0
        reasons = []
        
        # Trend analysis
        trend_direction = analysis["trend_direction"]
        sma_20 = analysis["sma_20"]
        sma_50 = analysis["sma_50"]
        sma_200 = analysis["sma_200"]
        rsi = analysis["rsi"]
        macd = analysis["macd"]
        bb_data = analysis["bollinger_bands"]
        price_position = analysis["price_position"]
        
        # Strong buy conditions
        if (trend_direction == "up" and 
            current_price > sma_20 > sma_50 > sma_200 and
            rsi < 70 and  # Not overbought
            macd["macd"] > macd["signal"] and
            price_position < 0.8):  # Not at upper Bollinger Band
            
            signal_type = SignalType.STRONG_BUY
            confidence = 85.0
            reasons.extend([
                "Strong uptrend confirmed by moving averages",
                "RSI indicates momentum without overbought conditions",
                "MACD shows bullish momentum",
                "Price not at resistance level"
            ])
        
        # Buy conditions
        elif (trend_direction == "up" and
              current_price > sma_50 and
              rsi < 75 and
              macd["macd"] > macd["signal"]):
            
            signal_type = SignalType.BUY
            confidence = 70.0
            reasons.extend([
                "Uptrend confirmed",
                "RSI in healthy range",
                "MACD bullish"
            ])
        
        # Strong sell conditions
        elif (trend_direction == "down" and
              current_price < sma_20 < sma_50 < sma_200 and
              rsi > 30 and  # Not oversold
              macd["macd"] < macd["signal"] and
              price_position > 0.2):  # Not at lower Bollinger Band
            
            signal_type = SignalType.STRONG_SELL
            confidence = 85.0
            reasons.extend([
                "Strong downtrend confirmed by moving averages",
                "RSI indicates momentum without oversold conditions",
                "MACD shows bearish momentum",
                "Price not at support level"
            ])
        
        # Sell conditions
        elif (trend_direction == "down" and
              current_price < sma_50 and
              rsi > 25 and
              macd["macd"] < macd["signal"]):
            
            signal_type = SignalType.SELL
            confidence = 70.0
            reasons.extend([
                "Downtrend confirmed",
                "RSI in bearish range",
                "MACD bearish"
            ])
        
        # Hold conditions
        else:
            signal_type = SignalType.HOLD
            confidence = 60.0
            reasons.append("Mixed signals - waiting for clearer trend confirmation")
        
        # Adjust confidence based on risk level
        if risk_level == RiskLevel.CONSERVATIVE:
            confidence *= 0.8  # More conservative
        elif risk_level == RiskLevel.AGGRESSIVE:
            confidence *= 1.2  # More aggressive
        
        return TradingSignal(
            symbol=symbol,
            signal_type=signal_type,
            confidence=min(100, confidence),
            price=current_price,
            reasons=reasons,
            technical_analysis=analysis
        )
    
    async def _add_risk_management(
        self, 
        signal: TradingSignal, 
        current_price: float, 
        analysis: Dict[str, Any], 
        risk_level: RiskLevel,
        position_size: float
    ) -> TradingSignal:
        """Add risk management parameters to the signal."""
        
        atr = analysis["atr"]
        bb_data = analysis["bollinger_bands"]
        
        # Calculate stop loss based on ATR and risk level
        if risk_level == RiskLevel.CONSERVATIVE:
            stop_loss_multiplier = 2.0
        elif risk_level == RiskLevel.MODERATE:
            stop_loss_multiplier = 1.5
        else:  # AGGRESSIVE
            stop_loss_multiplier = 1.0
        
        # Set stop loss and take profit
        if signal.signal_type in [SignalType.BUY, SignalType.STRONG_BUY]:
            stop_loss = current_price - (atr * stop_loss_multiplier)
            take_profit = current_price + (atr * stop_loss_multiplier * 2)  # 2:1 risk/reward
            target_price = current_price + (atr * stop_loss_multiplier * 1.5)
        elif signal.signal_type in [SignalType.SELL, SignalType.STRONG_SELL]:
            stop_loss = current_price + (atr * stop_loss_multiplier)
            take_profit = current_price - (atr * stop_loss_multiplier * 2)
            target_price = current_price - (atr * stop_loss_multiplier * 1.5)
        else:
            stop_loss = None
            take_profit = None
            target_price = None
        
        # Calculate risk/reward ratio
        if stop_loss and target_price:
            risk = abs(current_price - stop_loss)
            reward = abs(target_price - current_price)
            risk_reward_ratio = reward / risk if risk > 0 else 0
        else:
            risk_reward_ratio = None
        
        # Adjust position size based on confidence and risk level
        adjusted_position_size = position_size * (signal.confidence / 100)
        
        # Update signal with risk management parameters
        signal.stop_loss = stop_loss
        signal.take_profit = take_profit
        signal.target_price = target_price
        signal.risk_reward_ratio = risk_reward_ratio
        signal.position_size = adjusted_position_size
        
        return signal
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, float]:
        """Calculate MACD."""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line.iloc[-1],
            "signal": signal_line.iloc[-1],
            "histogram": histogram.iloc[-1]
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands."""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            "upper": upper.iloc[-1],
            "middle": middle.iloc[-1],
            "lower": lower.iloc[-1]
        }
    
    def _calculate_atr(self, hist: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range."""
        high_low = hist['High'] - hist['Low']
        high_close = np.abs(hist['High'] - hist['Close'].shift())
        low_close = np.abs(hist['Low'] - hist['Close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean()
        
        return atr.iloc[-1]


class SignalBacktestTool(Tool):
    """Tool for backtesting trading signals."""
    
    name = "backtest_signals"
    description = "Backtest trading signals to evaluate strategy performance"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the signal backtest tool."""
        try:
            symbol = params.get("symbol", "").upper()
            start_date = params.get("start_date", "2023-01-01")
            end_date = params.get("end_date", "2024-01-01")
            initial_capital = params.get("initial_capital", 100000)
            position_size = params.get("position_size", 0.1)
            
            if not symbol:
                return {"error": "Symbol is required"}
            
            # Get historical data
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                return {"error": f"No data found for symbol {symbol}"}
            
            # Run backtest
            backtest_results = await self._run_backtest(hist, initial_capital, position_size)
            
            return {
                "success": True,
                "backtest_results": backtest_results,
                "message": f"Backtest completed for {symbol}"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to run backtest: {str(e)}",
                "success": False
            }
    
    async def _run_backtest(self, hist: pd.DataFrame, initial_capital: float, position_size: float) -> Dict[str, Any]:
        """Run backtest simulation."""
        # This is a simplified backtest implementation
        # In a real implementation, you would use more sophisticated backtesting
        
        capital = initial_capital
        shares = 0
        trades = []
        
        for i in range(50, len(hist)):  # Start after 50 days for moving averages
            current_data = hist.iloc[:i+1]
            current_price = current_data['Close'].iloc[-1]
            
            # Generate signal for this point
            signal = await self._generate_historical_signal(current_data)
            
            # Execute trades based on signal
            if signal == "buy" and shares == 0:
                shares = int((capital * position_size) / current_price)
                capital -= shares * current_price
                trades.append({
                    "date": current_data.index[-1],
                    "action": "buy",
                    "price": current_price,
                    "shares": shares
                })
            
            elif signal == "sell" and shares > 0:
                capital += shares * current_price
                trades.append({
                    "date": current_data.index[-1],
                    "action": "sell",
                    "price": current_price,
                    "shares": shares
                })
                shares = 0
        
        # Calculate final portfolio value
        final_value = capital + (shares * hist['Close'].iloc[-1])
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        return {
            "initial_capital": initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "total_trades": len(trades),
            "trades": trades
        }
    
    async def _generate_historical_signal(self, hist: pd.DataFrame) -> str:
        """Generate signal for historical data point."""
        # Simplified signal generation for backtesting
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
        
        if current_price > sma_20 > sma_50:
            return "buy"
        elif current_price < sma_20 < sma_50:
            return "sell"
        else:
            return "hold"
