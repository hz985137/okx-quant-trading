"""相对强弱指数(RSI)策略"""

import pandas as pd
from typing import Optional
from .base_strategy import BaseStrategy
from utils.indicators import calculate_rsi
from utils.logger import logger


class RSIStrategy(BaseStrategy):
    """
    RSI策略
    RSI < 30 为超卖信号，买入
    RSI > 70 为超买信号，卖出
    """
    
    def __init__(self, symbol: str, timeframe: str = "1h", period: int = 14, 
                 oversold: float = 30, overbought: float = 70):
        """
        初始化RSI策略
        
        Args:
            symbol: 交易对
            timeframe: K线周期
            period: RSI计算周期
            oversold: 超卖阈值
            overbought: 超买阈值
        """
        super().__init__("RSIStrategy", symbol, timeframe)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        
        logger.info(f"RSI策略初始化: period={period}, oversold={oversold}, overbought={overbought}")
    
    def calculate_signal(self, data: pd.DataFrame) -> str:
        """
        计算RSI交易信号
        
        Args:
            data: 包含close列的DataFrame
            
        Returns:
            "buy", "sell" 或 "hold"
        """
        if len(data) < self.period + 1:
            return "hold"
        
        # 计算RSI
        rsi = calculate_rsi(data['close'], self.period)
        current_rsi = rsi.iloc[-1]
        
        # 超卖买入
        if current_rsi < self.oversold and not self.is_trading:
            return "buy"
        
        # 超买卖出
        if current_rsi > self.overbought and self.is_trading:
            return "sell"
        
        return "hold"
