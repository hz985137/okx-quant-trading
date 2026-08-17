"""移动平均线(MA)策略"""

import pandas as pd
from typing import Optional
from .base_strategy import BaseStrategy
from utils.indicators import calculate_ma
from utils.logger import logger


class MAStrategy(BaseStrategy):
    """
    移动平均线策略
    快线向上穿过慢线为买入信号
    快线向下穿过慢线为卖出信号
    """
    
    def __init__(self, symbol: str, timeframe: str = "1h", fast_period: int = 10, slow_period: int = 30):
        """
        初始化MA策略
        
        Args:
            symbol: 交易对
            timeframe: K线周期
            fast_period: 快线周期
            slow_period: 慢线周期
        """
        super().__init__("MAStrategy", symbol, timeframe)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.last_signal = None
        
        logger.info(f"MA策略初始化: fast={fast_period}, slow={slow_period}")
    
    def calculate_signal(self, data: pd.DataFrame) -> str:
        """
        计算MA交易信号
        
        Args:
            data: 包含close列的DataFrame
            
        Returns:
            "buy", "sell" 或 "hold"
        """
        if len(data) < self.slow_period:
            return "hold"
        
        # 计算移动平均线
        data['fast_ma'] = calculate_ma(data['close'], self.fast_period)
        data['slow_ma'] = calculate_ma(data['close'], self.slow_period)
        
        fast_ma = data['fast_ma'].iloc[-1]
        slow_ma = data['slow_ma'].iloc[-1]
        prev_fast_ma = data['fast_ma'].iloc[-2] if len(data) > 1 else fast_ma
        prev_slow_ma = data['slow_ma'].iloc[-2] if len(data) > 1 else slow_ma
        
        # 金叉：快线从下向上穿过慢线
        if prev_fast_ma <= prev_slow_ma and fast_ma > slow_ma:
            self.last_signal = "buy"
            return "buy"
        
        # 死叉：快线从上向下穿过慢线
        if prev_fast_ma >= prev_slow_ma and fast_ma < slow_ma:
            self.last_signal = "sell"
            return "sell"
        
        return "hold"
