"""Configuration Management."""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    """Application configuration."""
    
    # Application settings
    app_name: str = Field(default="trend-following-mcp", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # API settings
    yahoo_finance_api_key: Optional[str] = Field(default=None, description="Yahoo Finance API key")
    alpha_vantage_api_key: Optional[str] = Field(default=None, description="Alpha Vantage API key")
    
    # Database settings
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    
    # MCP Server settings
    mcp_server_host: str = Field(default="localhost", description="MCP server host")
    mcp_server_port: int = Field(default=8000, description="MCP server port")
    mcp_server_debug: bool = Field(default=False, description="MCP server debug mode")
    
    # Trading settings
    default_risk_level: str = Field(default="moderate", description="Default risk level")
    default_position_size: float = Field(default=0.1, description="Default position size")
    max_position_size: float = Field(default=0.25, description="Maximum position size")
    
    # Technical analysis settings
    default_lookback_period: int = Field(default=252, description="Default lookback period (days)")
    rsi_period: int = Field(default=14, description="RSI calculation period")
    macd_fast: int = Field(default=12, description="MACD fast period")
    macd_slow: int = Field(default=26, description="MACD slow period")
    macd_signal: int = Field(default=9, description="MACD signal period")
    bollinger_period: int = Field(default=20, description="Bollinger Bands period")
    bollinger_std: int = Field(default=2, description="Bollinger Bands standard deviation")
    
    # Risk management settings
    stop_loss_multiplier: float = Field(default=1.5, description="Stop loss ATR multiplier")
    take_profit_multiplier: float = Field(default=2.0, description="Take profit ATR multiplier")
    max_drawdown_limit: float = Field(default=0.15, description="Maximum drawdown limit")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # Cache settings
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        """Initialize configuration."""
        # Load environment variables
        load_dotenv()
        
        super().__init__(**kwargs)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or os.getenv("ENVIRONMENT") == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug and os.getenv("ENVIRONMENT") == "production"
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service."""
        api_keys = {
            "yahoo_finance": self.yahoo_finance_api_key,
            "alpha_vantage": self.alpha_vantage_api_key,
        }
        return api_keys.get(service)
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Get trading configuration."""
        return {
            "default_risk_level": self.default_risk_level,
            "default_position_size": self.default_position_size,
            "max_position_size": self.max_position_size,
            "stop_loss_multiplier": self.stop_loss_multiplier,
            "take_profit_multiplier": self.take_profit_multiplier,
            "max_drawdown_limit": self.max_drawdown_limit,
        }
    
    def get_technical_config(self) -> Dict[str, Any]:
        """Get technical analysis configuration."""
        return {
            "default_lookback_period": self.default_lookback_period,
            "rsi_period": self.rsi_period,
            "macd_fast": self.macd_fast,
            "macd_slow": self.macd_slow,
            "macd_signal": self.macd_signal,
            "bollinger_period": self.bollinger_period,
            "bollinger_std": self.bollinger_std,
        }
    
    def validate(self) -> bool:
        """Validate configuration."""
        # Check required settings
        if not self.database_url and self.is_production:
            raise ValueError("Database URL is required in production")
        
        # Validate trading settings
        if not 0 < self.default_position_size <= self.max_position_size:
            raise ValueError("Invalid position size configuration")
        
        if self.max_drawdown_limit <= 0 or self.max_drawdown_limit > 1:
            raise ValueError("Invalid max drawdown limit")
        
        # Validate technical analysis settings
        if self.rsi_period <= 0:
            raise ValueError("Invalid RSI period")
        
        if self.macd_fast >= self.macd_slow:
            raise ValueError("MACD fast period must be less than slow period")
        
        return True


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get global configuration instance."""
    return config


def reload_config() -> Config:
    """Reload configuration from environment."""
    global config
    config = Config()
    return config
