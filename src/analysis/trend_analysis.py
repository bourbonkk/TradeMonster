"""Trend Analysis Engine."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

from ..mcp.schemas import TrendDirection


class TrendAnalyzer:
    """Analyze market trends using various technical indicators."""
    
    def __init__(self):
        """Initialize the trend analyzer."""
        self.trend_periods = [20, 50, 200]  # Short, medium, long term
        self.confidence_thresholds = {
            "strong": 0.8,
            "moderate": 0.6,
            "weak": 0.4
        }
    
    def analyze_trend(self, prices: pd.Series, volume: pd.Series = None) -> Dict[str, Any]:
        """Analyze trend direction and strength."""
        if len(prices) < max(self.trend_periods):
            return {"error": "Insufficient data for trend analysis"}
        
        # Calculate moving averages
        moving_averages = self._calculate_moving_averages(prices)
        
        # Determine trend direction
        trend_direction = self._determine_trend_direction(prices, moving_averages)
        
        # Calculate trend strength
        trend_strength = self._calculate_trend_strength(prices, moving_averages)
        
        # Analyze trend consistency
        trend_consistency = self._analyze_trend_consistency(prices, moving_averages)
        
        # Volume analysis if available
        volume_analysis = {}
        if volume is not None:
            volume_analysis = self._analyze_volume_trend(volume, prices)
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "trend_consistency": trend_consistency,
            "moving_averages": moving_averages,
            "volume_analysis": volume_analysis,
            "support_resistance": self._find_support_resistance(prices),
            "trend_duration": self._calculate_trend_duration(prices, trend_direction)
        }
    
    def _calculate_moving_averages(self, prices: pd.Series) -> Dict[str, float]:
        """Calculate moving averages for different periods."""
        moving_averages = {}
        
        for period in self.trend_periods:
            if len(prices) >= period:
                moving_averages[f"sma_{period}"] = prices.rolling(window=period).mean().iloc[-1]
                moving_averages[f"ema_{period}"] = prices.ewm(span=period).mean().iloc[-1]
        
        return moving_averages
    
    def _determine_trend_direction(self, prices: pd.Series, moving_averages: Dict[str, float]) -> TrendDirection:
        """Determine the overall trend direction."""
        current_price = prices.iloc[-1]
        
        # Check if we have enough moving averages
        if "sma_50" not in moving_averages or "sma_200" not in moving_averages:
            return TrendDirection.SIDEWAYS
        
        sma_20 = moving_averages.get("sma_20", current_price)
        sma_50 = moving_averages["sma_50"]
        sma_200 = moving_averages["sma_200"]
        
        # Strong uptrend: price > SMA20 > SMA50 > SMA200
        if current_price > sma_20 > sma_50 > sma_200:
            return TrendDirection.UP
        
        # Strong downtrend: price < SMA20 < SMA50 < SMA200
        elif current_price < sma_20 < sma_50 < sma_200:
            return TrendDirection.DOWN
        
        # Weak uptrend: price > SMA50 > SMA200
        elif current_price > sma_50 > sma_200:
            return TrendDirection.UP
        
        # Weak downtrend: price < SMA50 < SMA200
        elif current_price < sma_50 < sma_200:
            return TrendDirection.DOWN
        
        # Sideways: mixed signals
        else:
            return TrendDirection.SIDEWAYS
    
    def _calculate_trend_strength(self, prices: pd.Series, moving_averages: Dict[str, float]) -> float:
        """Calculate trend strength (0-100)."""
        if len(prices) < 50:
            return 50.0
        
        current_price = prices.iloc[-1]
        
        # Price position relative to moving averages
        price_above_ma = 0
        total_ma = 0
        
        for period in self.trend_periods:
            sma_key = f"sma_{period}"
            if sma_key in moving_averages:
                total_ma += 1
                if current_price > moving_averages[sma_key]:
                    price_above_ma += 1
        
        ma_score = (price_above_ma / total_ma) * 100 if total_ma > 0 else 50
        
        # Price momentum (recent price change)
        price_change_20d = (current_price / prices.iloc[-20] - 1) * 100 if len(prices) >= 20 else 0
        price_change_50d = (current_price / prices.iloc[-50] - 1) * 100 if len(prices) >= 50 else 0
        
        momentum_score = (abs(price_change_20d) + abs(price_change_50d)) / 2
        
        # Linear regression slope
        slope_score = self._calculate_linear_regression_slope(prices)
        
        # Combine scores
        trend_strength = (ma_score * 0.4 + momentum_score * 0.3 + slope_score * 0.3)
        
        return min(100, max(0, trend_strength))
    
    def _calculate_linear_regression_slope(self, prices: pd.Series) -> float:
        """Calculate linear regression slope for trend strength."""
        if len(prices) < 20:
            return 50.0
        
        # Use last 20 periods for regression
        recent_prices = prices.tail(20)
        x = np.arange(len(recent_prices))
        y = recent_prices.values
        
        # Simple linear regression
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalize slope to 0-100 scale
        price_range = recent_prices.max() - recent_prices.min()
        if price_range > 0:
            normalized_slope = (slope / price_range) * 100
            return min(100, max(0, normalized_slope + 50))
        else:
            return 50.0
    
    def _analyze_trend_consistency(self, prices: pd.Series, moving_averages: Dict[str, float]) -> Dict[str, Any]:
        """Analyze how consistent the trend has been."""
        if len(prices) < 50:
            return {"consistency": 0.5, "reversals": 0}
        
        # Count trend reversals
        reversals = 0
        current_trend = None
        
        for i in range(20, len(prices)):
            if "sma_50" in moving_averages:
                sma_50 = prices.rolling(window=50).mean().iloc[i]
                price = prices.iloc[i]
                
                if price > sma_50:
                    if current_trend == "down":
                        reversals += 1
                    current_trend = "up"
                elif price < sma_50:
                    if current_trend == "up":
                        reversals += 1
                    current_trend = "down"
        
        # Calculate consistency score
        total_periods = len(prices) - 20
        consistency = 1 - (reversals / total_periods) if total_periods > 0 else 0
        
        return {
            "consistency": consistency,
            "reversals": reversals,
            "total_periods": total_periods
        }
    
    def _analyze_volume_trend(self, volume: pd.Series, prices: pd.Series) -> Dict[str, Any]:
        """Analyze volume trend and its relationship with price."""
        if len(volume) < 20:
            return {}
        
        # Volume moving average
        volume_sma = volume.rolling(window=20).mean().iloc[-1]
        current_volume = volume.iloc[-1]
        
        # Volume trend
        volume_trend = "increasing" if current_volume > volume_sma else "decreasing"
        
        # Price-volume relationship
        price_change = (prices.iloc[-1] / prices.iloc[-2] - 1) if len(prices) > 1 else 0
        volume_change = (current_volume / volume.iloc[-2] - 1) if len(volume) > 1 else 0
        
        # Volume confirmation
        volume_confirms_trend = (
            (price_change > 0 and volume_change > 0) or
            (price_change < 0 and volume_change > 0)
        )
        
        return {
            "volume_trend": volume_trend,
            "volume_ratio": current_volume / volume_sma,
            "volume_confirms_trend": volume_confirms_trend,
            "price_volume_correlation": self._calculate_price_volume_correlation(prices, volume)
        }
    
    def _calculate_price_volume_correlation(self, prices: pd.Series, volume: pd.Series) -> float:
        """Calculate correlation between price and volume."""
        if len(prices) < 20 or len(volume) < 20:
            return 0.0
        
        # Use last 20 periods
        recent_prices = prices.tail(20)
        recent_volume = volume.tail(20)
        
        # Calculate correlation
        correlation = recent_prices.corr(recent_volume)
        return correlation if not pd.isna(correlation) else 0.0
    
    def _find_support_resistance(self, prices: pd.Series) -> Dict[str, float]:
        """Find support and resistance levels."""
        if len(prices) < 50:
            return {"support": prices.min(), "resistance": prices.max()}
        
        # Use recent 50 periods
        recent_prices = prices.tail(50)
        
        # Find local minima and maxima
        highs = recent_prices.rolling(window=5, center=True).max()
        lows = recent_prices.rolling(window=5, center=True).min()
        
        # Find resistance (recent highs)
        resistance_levels = highs.nlargest(3).unique()
        resistance = resistance_levels[0] if len(resistance_levels) > 0 else recent_prices.max()
        
        # Find support (recent lows)
        support_levels = lows.nsmallest(3).unique()
        support = support_levels[0] if len(support_levels) > 0 else recent_prices.min()
        
        return {
            "support": support,
            "resistance": resistance,
            "support_levels": support_levels.tolist() if len(support_levels) > 0 else [],
            "resistance_levels": resistance_levels.tolist() if len(resistance_levels) > 0 else []
        }
    
    def _calculate_trend_duration(self, prices: pd.Series, trend_direction: TrendDirection) -> int:
        """Calculate how long the current trend has been in place."""
        if len(prices) < 20:
            return 0
        
        duration = 0
        current_price = prices.iloc[-1]
        
        # Count consecutive periods in the same direction
        for i in range(len(prices) - 1, 0, -1):
            if trend_direction == TrendDirection.UP:
                if prices.iloc[i] > prices.iloc[i-1]:
                    duration += 1
                else:
                    break
            elif trend_direction == TrendDirection.DOWN:
                if prices.iloc[i] < prices.iloc[i-1]:
                    duration += 1
                else:
                    break
            else:
                break
        
        return duration
    
    def get_trend_forecast(self, prices: pd.Series, periods: int = 10) -> Dict[str, Any]:
        """Generate trend forecast for the next N periods."""
        if len(prices) < 50:
            return {"error": "Insufficient data for forecasting"}
        
        # Simple linear regression forecast
        recent_prices = prices.tail(20)
        x = np.arange(len(recent_prices))
        y = recent_prices.values
        
        # Fit linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Generate forecast
        forecast_x = np.arange(len(recent_prices), len(recent_prices) + periods)
        forecast_prices = slope * forecast_x + intercept
        
        # Calculate confidence intervals (simplified)
        residuals = y - (slope * x + intercept)
        std_error = np.std(residuals)
        
        upper_bound = forecast_prices + (1.96 * std_error)
        lower_bound = forecast_prices - (1.96 * std_error)
        
        return {
            "forecast_prices": forecast_prices.tolist(),
            "upper_bound": upper_bound.tolist(),
            "lower_bound": lower_bound.tolist(),
            "slope": slope,
            "confidence": 0.95
        }
