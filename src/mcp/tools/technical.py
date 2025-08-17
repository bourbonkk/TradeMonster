"""Technical Analysis MCP Tool."""

import asyncio
from typing import Dict, Any, Optional, List
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

from mcp import Tool
from ..schemas import TechnicalIndicators, TrendDirection


class TechnicalAnalysisTool(Tool):
    """Tool for performing technical analysis on stocks."""
    
    name = "analyze_technical"
    description = "Perform comprehensive technical analysis including moving averages, momentum, and volatility indicators"
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the technical analysis tool."""
        try:
            symbol = params.get("symbol", "").upper()
            period = params.get("period", "1y")
            indicators = params.get("indicators", ["sma", "rsi", "macd", "bollinger"])
            
            if not symbol:
                return {"error": "Symbol is required"}
            
            # Get historical data
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if hist.empty:
                return {"error": f"No data found for symbol {symbol}"}
            
            # Calculate technical indicators
            technical_data = await self._calculate_indicators(hist, indicators)
            
            # Determine trend direction and strength
            trend_analysis = await self._analyze_trend(hist, technical_data)
            
            # Create technical indicators object
            latest_data = hist.iloc[-1]
            technical_indicators = TechnicalIndicators(
                symbol=symbol,
                date=latest_data.name.date(),
                sma_20=technical_data.get("sma_20", 0),
                sma_50=technical_data.get("sma_50", 0),
                sma_200=technical_data.get("sma_200", 0),
                ema_12=technical_data.get("ema_12", 0),
                ema_26=technical_data.get("ema_26", 0),
                rsi=technical_data.get("rsi", 0),
                macd=technical_data.get("macd", 0),
                macd_signal=technical_data.get("macd_signal", 0),
                macd_histogram=technical_data.get("macd_histogram", 0),
                stoch_k=technical_data.get("stoch_k", 0),
                stoch_d=technical_data.get("stoch_d", 0),
                bollinger_upper=technical_data.get("bollinger_upper", 0),
                bollinger_middle=technical_data.get("bollinger_middle", 0),
                bollinger_lower=technical_data.get("bollinger_lower", 0),
                atr=technical_data.get("atr", 0),
                obv=technical_data.get("obv", 0),
                volume_sma=technical_data.get("volume_sma", 0),
                trend_direction=trend_analysis["direction"],
                trend_strength=trend_analysis["strength"]
            )
            
            return {
                "success": True,
                "technical_indicators": technical_indicators.model_dump(),
                "analysis_summary": await self._generate_analysis_summary(technical_indicators),
                "signal_strength": await self._calculate_signal_strength(technical_indicators),
                "message": f"Technical analysis completed for {symbol}"
            }
            
        except Exception as e:
            return {
                "error": f"Failed to perform technical analysis: {str(e)}",
                "success": False
            }
    
    async def _calculate_indicators(self, hist: pd.DataFrame, indicators: List[str]) -> Dict[str, float]:
        """Calculate technical indicators."""
        result = {}
        
        if "sma" in indicators:
            result["sma_20"] = hist['Close'].rolling(window=20).mean().iloc[-1]
            result["sma_50"] = hist['Close'].rolling(window=50).mean().iloc[-1]
            result["sma_200"] = hist['Close'].rolling(window=200).mean().iloc[-1]
        
        if "ema" in indicators:
            result["ema_12"] = hist['Close'].ewm(span=12).mean().iloc[-1]
            result["ema_26"] = hist['Close'].ewm(span=26).mean().iloc[-1]
        
        if "rsi" in indicators:
            result["rsi"] = self._calculate_rsi(hist['Close'])
        
        if "macd" in indicators:
            macd_data = self._calculate_macd(hist['Close'])
            result["macd"] = macd_data["macd"]
            result["macd_signal"] = macd_data["signal"]
            result["macd_histogram"] = macd_data["histogram"]
        
        if "stochastic" in indicators:
            stoch_data = self._calculate_stochastic(hist)
            result["stoch_k"] = stoch_data["k"]
            result["stoch_d"] = stoch_data["d"]
        
        if "bollinger" in indicators:
            bb_data = self._calculate_bollinger_bands(hist['Close'])
            result["bollinger_upper"] = bb_data["upper"]
            result["bollinger_middle"] = bb_data["middle"]
            result["bollinger_lower"] = bb_data["lower"]
        
        if "atr" in indicators:
            result["atr"] = self._calculate_atr(hist)
        
        if "volume" in indicators:
            result["obv"] = self._calculate_obv(hist)
            result["volume_sma"] = hist['Volume'].rolling(window=20).mean().iloc[-1]
        
        return result
    
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
    
    def _calculate_stochastic(self, hist: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, float]:
        """Calculate Stochastic Oscillator."""
        low_min = hist['Low'].rolling(window=k_period).min()
        high_max = hist['High'].rolling(window=k_period).max()
        k_percent = 100 * ((hist['Close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            "k": k_percent.iloc[-1],
            "d": d_percent.iloc[-1]
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
    
    def _calculate_obv(self, hist: pd.DataFrame) -> float:
        """Calculate On-Balance Volume."""
        obv = pd.Series(index=hist.index, dtype=float)
        obv.iloc[0] = hist['Volume'].iloc[0]
        
        for i in range(1, len(hist)):
            if hist['Close'].iloc[i] > hist['Close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + hist['Volume'].iloc[i]
            elif hist['Close'].iloc[i] < hist['Close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - hist['Volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv.iloc[-1]
    
    async def _analyze_trend(self, hist: pd.DataFrame, technical_data: Dict[str, float]) -> Dict[str, Any]:
        """Analyze trend direction and strength."""
        current_price = hist['Close'].iloc[-1]
        sma_50 = technical_data.get("sma_50", current_price)
        sma_200 = technical_data.get("sma_200", current_price)
        
        # Determine trend direction
        if current_price > sma_50 > sma_200:
            direction = TrendDirection.UP
        elif current_price < sma_50 < sma_200:
            direction = TrendDirection.DOWN
        else:
            direction = TrendDirection.SIDEWAYS
        
        # Calculate trend strength (0-100)
        price_change_20d = (current_price / hist['Close'].iloc[-20] - 1) * 100 if len(hist) >= 20 else 0
        price_change_50d = (current_price / hist['Close'].iloc[-50] - 1) * 100 if len(hist) >= 50 else 0
        
        # Combine multiple factors for strength calculation
        strength_factors = [
            abs(price_change_20d) * 0.4,
            abs(price_change_50d) * 0.3,
            abs(technical_data.get("rsi", 50) - 50) * 0.3
        ]
        
        strength = min(100, sum(strength_factors))
        
        return {
            "direction": direction,
            "strength": strength,
            "price_change_20d": price_change_20d,
            "price_change_50d": price_change_50d
        }
    
    async def _generate_analysis_summary(self, indicators: TechnicalIndicators) -> Dict[str, Any]:
        """Generate analysis summary."""
        summary = {
            "trend": {
                "direction": indicators.trend_direction.value,
                "strength": f"{indicators.trend_strength:.1f}%"
            },
            "momentum": {
                "rsi_status": "Oversold" if indicators.rsi < 30 else "Overbought" if indicators.rsi > 70 else "Neutral",
                "macd_signal": "Bullish" if indicators.macd > indicators.macd_signal else "Bearish",
                "stochastic_status": "Oversold" if indicators.stoch_k < 20 else "Overbought" if indicators.stoch_k > 80 else "Neutral"
            },
            "volatility": {
                "bollinger_position": "Upper Band" if indicators.bollinger_upper < indicators.bollinger_upper else "Lower Band" if indicators.bollinger_lower > indicators.bollinger_lower else "Middle",
                "atr_level": f"{indicators.atr:.2f}"
            },
            "support_resistance": {
                "support": indicators.bollinger_lower,
                "resistance": indicators.bollinger_upper
            }
        }
        
        return summary
    
    async def _calculate_signal_strength(self, indicators: TechnicalIndicators) -> Dict[str, float]:
        """Calculate signal strength for different timeframes."""
        # This is a simplified signal strength calculation
        # In a real implementation, you would use more sophisticated algorithms
        
        bullish_signals = 0
        bearish_signals = 0
        total_signals = 0
        
        # RSI signals
        if indicators.rsi < 30:
            bullish_signals += 1
        elif indicators.rsi > 70:
            bearish_signals += 1
        total_signals += 1
        
        # MACD signals
        if indicators.macd > indicators.macd_signal:
            bullish_signals += 1
        else:
            bearish_signals += 1
        total_signals += 1
        
        # Moving average signals
        if indicators.sma_20 > indicators.sma_50:
            bullish_signals += 1
        else:
            bearish_signals += 1
        total_signals += 1
        
        # Trend direction
        if indicators.trend_direction == TrendDirection.UP:
            bullish_signals += 1
        elif indicators.trend_direction == TrendDirection.DOWN:
            bearish_signals += 1
        total_signals += 1
        
        bullish_strength = (bullish_signals / total_signals) * 100
        bearish_strength = (bearish_signals / total_signals) * 100
        
        return {
            "bullish_strength": bullish_strength,
            "bearish_strength": bearish_strength,
            "neutral_strength": 100 - bullish_strength - bearish_strength
        }
