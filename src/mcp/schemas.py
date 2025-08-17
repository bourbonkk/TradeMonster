"""Data schemas for the Trend Following MCP Server."""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field
from enum import Enum


class RiskLevel(str, Enum):
    """Risk tolerance levels."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class SignalType(str, Enum):
    """Trading signal types."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


class TrendDirection(str, Enum):
    """Trend direction."""
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"


class StockInfo(BaseModel):
    """Stock information model."""
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    pe_ratio: Optional[float] = Field(None, description="P/E ratio")
    price: float = Field(..., description="Current price")
    change: float = Field(..., description="Price change")
    change_percent: float = Field(..., description="Price change percentage")
    volume: int = Field(..., description="Trading volume")
    avg_volume: Optional[int] = Field(None, description="Average volume")
    high_52w: Optional[float] = Field(None, description="52-week high")
    low_52w: Optional[float] = Field(None, description="52-week low")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield")
    beta: Optional[float] = Field(None, description="Beta coefficient")
    last_updated: datetime = Field(default_factory=datetime.now)


class TechnicalIndicators(BaseModel):
    """Technical indicators model."""
    symbol: str = Field(..., description="Stock symbol")
    date: date = Field(..., description="Analysis date")
    
    # Moving averages
    sma_20: float = Field(..., description="20-day Simple Moving Average")
    sma_50: float = Field(..., description="50-day Simple Moving Average")
    sma_200: float = Field(..., description="200-day Simple Moving Average")
    ema_12: float = Field(..., description="12-day Exponential Moving Average")
    ema_26: float = Field(..., description="26-day Exponential Moving Average")
    
    # Momentum indicators
    rsi: float = Field(..., description="Relative Strength Index")
    macd: float = Field(..., description="MACD line")
    macd_signal: float = Field(..., description="MACD signal line")
    macd_histogram: float = Field(..., description="MACD histogram")
    stoch_k: float = Field(..., description="Stochastic %K")
    stoch_d: float = Field(..., description="Stochastic %D")
    
    # Volatility indicators
    bollinger_upper: float = Field(..., description="Bollinger Band upper")
    bollinger_middle: float = Field(..., description="Bollinger Band middle")
    bollinger_lower: float = Field(..., description="Bollinger Band lower")
    atr: float = Field(..., description="Average True Range")
    
    # Volume indicators
    obv: float = Field(..., description="On-Balance Volume")
    volume_sma: float = Field(..., description="Volume Simple Moving Average")
    
    # Trend analysis
    trend_direction: TrendDirection = Field(..., description="Current trend direction")
    trend_strength: float = Field(..., description="Trend strength (0-100)")
    
    last_updated: datetime = Field(default_factory=datetime.now)


class TradingSignal(BaseModel):
    """Trading signal model."""
    symbol: str = Field(..., description="Stock symbol")
    signal_type: SignalType = Field(..., description="Signal type")
    confidence: float = Field(..., description="Signal confidence (0-100)")
    price: float = Field(..., description="Current price")
    target_price: Optional[float] = Field(None, description="Target price")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")
    
    # Signal reasoning
    reasons: List[str] = Field(default_factory=list, description="Signal reasons")
    technical_analysis: Dict[str, Any] = Field(default_factory=dict, description="Technical analysis summary")
    
    # Risk metrics
    risk_reward_ratio: Optional[float] = Field(None, description="Risk/reward ratio")
    position_size: Optional[float] = Field(None, description="Recommended position size (%)")
    
    generated_at: datetime = Field(default_factory=datetime.now)


class PortfolioAllocation(BaseModel):
    """Portfolio allocation model."""
    symbol: str = Field(..., description="Stock symbol")
    weight: float = Field(..., description="Portfolio weight (%)")
    shares: int = Field(..., description="Number of shares")
    value: float = Field(..., description="Position value")
    cost_basis: float = Field(..., description="Average cost basis")
    current_price: float = Field(..., description="Current price")
    unrealized_pnl: float = Field(..., description="Unrealized P&L")
    unrealized_pnl_percent: float = Field(..., description="Unrealized P&L percentage")
    
    # Risk metrics
    beta_contribution: float = Field(..., description="Beta contribution to portfolio")
    volatility_contribution: float = Field(..., description="Volatility contribution")
    
    last_updated: datetime = Field(default_factory=datetime.now)


class PortfolioSummary(BaseModel):
    """Portfolio summary model."""
    total_value: float = Field(..., description="Total portfolio value")
    total_cost: float = Field(..., description="Total cost basis")
    total_pnl: float = Field(..., description="Total P&L")
    total_pnl_percent: float = Field(..., description="Total P&L percentage")
    
    # Risk metrics
    portfolio_beta: float = Field(..., description="Portfolio beta")
    portfolio_volatility: float = Field(..., description="Portfolio volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    
    # Allocation
    allocations: List[PortfolioAllocation] = Field(default_factory=list, description="Stock allocations")
    
    # Performance
    daily_return: float = Field(..., description="Daily return")
    weekly_return: float = Field(..., description="Weekly return")
    monthly_return: float = Field(..., description="Monthly return")
    yearly_return: float = Field(..., description="Yearly return")
    
    last_updated: datetime = Field(default_factory=datetime.now)


class BacktestResult(BaseModel):
    """Backtest result model."""
    symbol: str = Field(..., description="Stock symbol")
    start_date: date = Field(..., description="Backtest start date")
    end_date: date = Field(..., description="Backtest end date")
    
    # Performance metrics
    total_return: float = Field(..., description="Total return")
    annualized_return: float = Field(..., description="Annualized return")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    win_rate: float = Field(..., description="Win rate")
    
    # Trading statistics
    total_trades: int = Field(..., description="Total number of trades")
    winning_trades: int = Field(..., description="Number of winning trades")
    losing_trades: int = Field(..., description="Number of losing trades")
    avg_win: float = Field(..., description="Average winning trade")
    avg_loss: float = Field(..., description="Average losing trade")
    profit_factor: float = Field(..., description="Profit factor")
    
    # Risk metrics
    volatility: float = Field(..., description="Portfolio volatility")
    var_95: float = Field(..., description="95% Value at Risk")
    cvar_95: float = Field(..., description="95% Conditional Value at Risk")
    
    # Strategy parameters
    strategy_params: Dict[str, Any] = Field(default_factory=dict, description="Strategy parameters used")
    
    generated_at: datetime = Field(default_factory=datetime.now)
