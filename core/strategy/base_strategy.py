"""交易策略基类"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
import pandas as pd
from datetime import datetime
from utils.logger import logger


class BaseStrategy(ABC):
    """所有策略的基类"""
    
    def __init__(self, name: str, symbol: str, timeframe: str = "1h"):
        """
        初始化策略
        
        Args:
            name: 策略名称
            symbol: 交易对 (e.g., "BTC-USDT")
            timeframe: K线周期 (e.g., "1h", "4h", "1d")
        """
        self.name = name
        self.symbol = symbol
        self.timeframe = timeframe
        self.is_trading = False
        self.position = 0  # 当前持仓
        self.entry_price = 0  # 入场价格
        self.trades = []  # 交易记录
        
        logger.info(f"初始化策略: {name} - {symbol} ({timeframe})")
    
    @abstractmethod
    def calculate_signal(self, data: pd.DataFrame) -> str:
        """
        计算交易信号
        
        Args:
            data: 包含OHLCV数据的DataFrame
            
        Returns:
            "buy", "sell" 或 "hold"
        """
        pass
    
    def on_bar(self, bar: Dict) -> Optional[str]:
        """
        每根K线回调
        
        Args:
            bar: K线数据字典 {"open", "high", "low", "close", "volume", "time"}
            
        Returns:
            交易信号
        """
        # 转换为DataFrame格式
        df = pd.DataFrame([bar])
        signal = self.calculate_signal(df)
        return signal
    
    def on_buy(self, price: float, amount: float, time: datetime):
        """
        买入回调
        
        Args:
            price: 买入价格
            amount: 买入数量
            time: 买入时间
        """
        self.position += amount
        self.entry_price = price
        self.is_trading = True
        
        trade = {
            "type": "buy",
            "price": price,
            "amount": amount,
            "time": time,
            "value": price * amount
        }
        self.trades.append(trade)
        logger.info(f"[{self.name}] 买入: {amount} @ {price} = {price * amount}")
    
    def on_sell(self, price: float, amount: float, time: datetime) -> Tuple[float, float]:
        """
        卖出回调
        
        Args:
            price: 卖出价格
            amount: 卖出数量
            time: 卖出时间
            
        Returns:
            (利润, 利润率)
        """
        if self.position <= 0:
            logger.warning(f"[{self.name}] 无持仓，无法卖出")
            return 0, 0
        
        sell_value = price * amount
        buy_value = self.entry_price * amount
        profit = sell_value - buy_value
        profit_rate = (profit / buy_value * 100) if buy_value > 0 else 0
        
        self.position -= amount
        if self.position <= 0:
            self.is_trading = False
        
        trade = {
            "type": "sell",
            "price": price,
            "amount": amount,
            "time": time,
            "value": sell_value,
            "profit": profit,
            "profit_rate": profit_rate
        }
        self.trades.append(trade)
        logger.info(f"[{self.name}] 卖出: {amount} @ {price} | 盈亏: {profit:.2f} ({profit_rate:.2f}%)")
        
        return profit, profit_rate
    
    def get_stats(self) -> Dict:
        """
        获取策略统计信息
        
        Returns:
            统计数据字典
        """
        if not self.trades:
            return {}
        
        df = pd.DataFrame(self.trades)
        buy_trades = df[df['type'] == 'buy']
        sell_trades = df[df['type'] == 'sell']
        
        total_trades = len(self.trades)
        completed_trades = len(sell_trades)
        win_trades = len(sell_trades[sell_trades['profit'] > 0]) if len(sell_trades) > 0 else 0
        
        total_profit = sell_trades['profit'].sum() if len(sell_trades) > 0 else 0
        avg_profit = sell_trades['profit'].mean() if len(sell_trades) > 0 else 0
        win_rate = (win_trades / completed_trades * 100) if completed_trades > 0 else 0
        
        return {
            "strategy": self.name,
            "symbol": self.symbol,
            "total_trades": total_trades,
            "completed_trades": completed_trades,
            "win_trades": win_trades,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "avg_profit": avg_profit,
            "current_position": self.position
        }
    
    def reset(self):
        """重置策略状态"""
        self.is_trading = False
        self.position = 0
        self.entry_price = 0
        self.trades = []
        logger.info(f"[{self.name}] 策略已重置")
