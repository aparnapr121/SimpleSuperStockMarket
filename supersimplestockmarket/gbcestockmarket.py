from dataclasses import dataclass, field
import time
from enum import Enum
from collections import deque
from statistics import geometric_mean
from typing import Deque, Optional


@dataclass
class TradeType(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Trade:
    time_stamp: float
    quantity: float
    trade_type: TradeType
    price: float


@dataclass
class StockTrades:
    trades: Deque[Trade] = field(default_factory=deque)
    total_volume: float = 0.0
    total_price_volume: float = 0.0


class TradeRecorder:
    def __init__(self, window_size):
        self._trades = {}
        self._window_seconds = window_size

    def add(self, stock_symbol: str, time_stamp: float, quantity: float, trade_type: TradeType, price: float) -> None:
        if stock_symbol not in self._trades:
            self._trades[stock_symbol] = StockTrades()
        stock_trades: StockTrades = self._trades[stock_symbol]
        stock_trades.trades.append(Trade(time_stamp, quantity, trade_type, price))
        stock_trades.total_price_volume += quantity * price
        stock_trades.total_volume += quantity

        current_stock: StockTrades = self._trades[stock_symbol]
        while current_stock.trades and current_stock.trades[0].time_stamp < time.time() - self._window_seconds:
            old_trade = current_stock.trades.popleft()
            current_stock.total_price_volume -= old_trade.quantity * old_trade.price
            current_stock.total_volume -= old_trade.quantity

    def get_volume_weighted_stock_price(self, stock_symbol: str) -> float:
        if stock_symbol not in self._trades or not self._trades[stock_symbol].trades:
            return 0
        current_stock: StockTrades = self._trades[stock_symbol]
        return 0 if current_stock.total_volume == 0 else current_stock.total_price_volume / current_stock.total_volume


class StockType(Enum):
    COMMON = 1
    PREFERRED = 2


@dataclass
class StocksDividendData:
    type: StockType
    last_dividend: float
    fixed_dividend: Optional[float]
    par_value: float


class ExchangeData:
    _dividend_dict = {
                      'TEA': {'type': StockType.COMMON, 'last_dividend': 0, 'fixed_dividend': None, 'par_value': 100},
                      'POP': {'type': StockType.COMMON, 'last_dividend': 8, 'fixed_dividend': None, 'par_value': 100},
                      'ALE': {'type': StockType.COMMON, 'last_dividend': 23, 'fixed_dividend': None, 'par_value': 60},
                      'GIN': {'type': StockType.PREFERRED, 'last_dividend': 8, 'fixed_dividend': 2, 'par_value': 100},
                      'JOE': {'type': StockType.COMMON, 'last_dividend': 13, 'fixed_dividend': None, 'par_value': 250}
                      }
    _stocks_dividend_data = {key : StocksDividendData(**val) for key, val in _dividend_dict.items()}

    def __init__(self):
        self.name = 'Global Beverage Corporation Exchange'

    def get_stocks_dividend_data(self) -> dict[str, StocksDividendData]:
        return self._stocks_dividend_data


class GBCEStockMarket:
    """
    For a given stock
    1. given any price as input, calculate dividen yield
    2. Given any price as  input, calculate the P/E ratio
    3. Record a trade with timestamp, quantity, buy or sell indicator and price
    4. Calculate volume weighted stock pice based on trades in past 5 minute
    For all stocks
    5. Calculate GBCE All Share Index using gemoetric mean of volume weighted stock price for all stocks
    """
    def __init__(self, exchange_data: ExchangeData, trade_recorder: TradeRecorder):
        self._stocks_dividend_data = exchange_data.get_stocks_dividend_data()
        self._trade_recorder = trade_recorder

    def _get_stocks_details(self, stock_symbol: str) -> StocksDividendData:
        stock_details = self._stocks_dividend_data.get(stock_symbol)
        if not stock_details:
            raise ValueError(f'Stock symbol input {stock_symbol} is invalid')
        return stock_details

    def calculate_dividend_yield(self, stock_symbol: str, price: float) -> float:
        """
        This method calculates the dividend for stock given a price
        If the stock is a common stock dividen_yield = last_dividend/price
        If stock is a preferred stock, dividend yield = (par_value * fixed_dividend_percent/100)/price
        """
        stock_details = self._get_stocks_details(stock_symbol)
        if stock_details.type == StockType.COMMON:
            dividend_yield = stock_details.last_dividend/price
        elif stock_details.type == StockType.PREFERRED:
            dividend_yield = (stock_details.par_value * stock_details.fixed_dividend) / (100 * price)
        else:
            raise ValueError(f'Invalid stock type for {stock_symbol}, only preferred stocks and common stocks are supported')
        return dividend_yield

    def calculate_pe(self, stock_symbol: str, price: float) -> float:
        stock_details = self._get_stocks_details(stock_symbol)
        if stock_details.last_dividend == 0:
            return float('inf')
        return price/stock_details.last_dividend

    def record_trade(self, stock_symbol: str, time_stamp: float, quantity: float, trade_type: TradeType, price: float) -> None:
        self._trade_recorder.add(stock_symbol, time_stamp, quantity, trade_type, price)

    def calculate_volume_weighted_stock_price(self, stock_symbol: str) -> float:
        return self._trade_recorder.get_volume_weighted_stock_price(stock_symbol)

    def calculate_gbce_all_share_index(self) -> float:
        prices = [self.calculate_volume_weighted_stock_price(key) for key, val in self._stocks_dividend_data.items()]
        filtered_prices = [price for price in prices if price > 0]
        return geometric_mean(filtered_prices) if filtered_prices else 0
