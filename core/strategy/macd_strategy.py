"""MACD策略"""

import pandas as pd
from typing import Optional
from .base_strategy import BaseStrategy
from utils.indicators import calculate_macd
from utils.logger import logger


class MACDStrategy(BaseStrategy):
    """
    MACD策略
    DIF向上穿过DEA为买入信号
    DIF向下穿过DEA为卖出信号
    """
    
    def __init__(self, symbol: str, timeframe: str = "1h", 
                 fast: int = 12, slow: int = 26, signal: int = 9):
        """
        初始化MACD策略
        
        Args:
            symbol: 交易对
            timeframe: K线周期
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
        """
        super().__init__("MACDStrategy", symbol, timeframe)
        self.fast = fast
        self.slow = slow
        self.signal = signal
        
        logger.info(f"MACD策略初始化: fast={fast}, slow={slow}, signal={signal}")
    
    def calculate_signal(self, data: pd.DataFrame) -> str:
        """
        计算MACD交易信号
        
        Args:
            data: 包含close列的DataFrame
            
        Returns:
            "buy", "sell" 或 "hold"
        """
        if len(data) < self.slow + self.signal:
            return "hold"
        
        # 计算MACD
        dif, dea, histogram = calculate_macd(data['close'], self.fast, self.slow, self.signal)
        
        current_dif = dif.iloc[-1]
        current_dea = dea.iloc[-1]
        prev_dif = dif.iloc[-2] if len(dif) > 1 else current_dif
        prev_dea = dea.iloc[-2] if len(dea) > 1 else current_dea
        
        # DIF向上穿过DEA
        if prev_dif <= prev_dea and current_dif > current_dea:
            return "buy"
        
        # DIF向下穿过DEA
        if prev_dif >= prev_dea and current_dif < current_dea:
            return "sell"
        
        return "hold"
