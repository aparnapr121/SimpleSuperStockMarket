import math
import statistics
import time
from time import sleep

from stockmarket.gbcestockmarket import GBCEStockMarket, ExchangeData, TradeRecorder
import pytest


class TestGBCEStockMarket:
    @classmethod
    def setup_class(cls):
        cls.test_stock_market = GBCEStockMarket(ExchangeData(), TradeRecorder(30))

    @pytest.mark.parametrize("stock_symbol, price, expected_dividend", [("TEA", 100, 0), ("POP", 100, .08),
                                                                        ("ALE", 100, .23), ("JOE", 100, .13),
                                                                        ("GIN", 250, .008)])
    def test_calculate_dividend_yield(self, stock_symbol, price, expected_dividend):
        actual_dividend = self.test_stock_market.calculate_dividend_yield(stock_symbol, price)
        assert actual_dividend == expected_dividend

    @pytest.mark.parametrize("stock_symbol, price, expected_dividend", [("HJI", 100, 0)])
    def test_calculate_dividend_yield_invalid_stock(self, stock_symbol, price, expected_dividend):
        with pytest.raises(ValueError):
            self.test_stock_market.calculate_dividend_yield(stock_symbol, price)

    @pytest.mark.parametrize("stock_symbol, price, expected_dividend", [("HJI", 0, 0)])
    def test_calculate_dividend_yield_zero_price(self, stock_symbol, price, expected_dividend):
        with pytest.raises(ValueError):
            self.test_stock_market.calculate_dividend_yield(stock_symbol, price)

    @pytest.mark.parametrize("stock_symbol, price, expected_pe", [("TEA", 100, float('inf')), ("POP", 138, 17.25),
                                                       ("ALE", 250, 10.86), ("JOE", 178, 13.69),
                                                       ("GIN", 250, 31.25), ("POP", 0, 0)])
    def test_calculate_pe(self, stock_symbol, price, expected_pe):
        actual_pe = self.test_stock_market.calculate_pe(stock_symbol, price)
        assert actual_pe == pytest.approx(expected_pe, rel=1e-2)

    def test_calculate_volume_weighted_stock_price(self):
        self.test_stock_market.record_trade("FIR", time.time()-30, 10, "BUY", 150 )
        self.test_stock_market.record_trade("FIR", time.time(), 20, "BUY", 160)
        self.test_stock_market.record_trade("FIR", time.time(), 30, "BUY", 170)
        self.test_stock_market.record_trade("FIR", time.time(), 40, "SELL", 180)
        expected_vwap = (20 * 160 + 30 * 170 + 40 * 180) / (20 + 30 + 40)
        actual_vwap = self.test_stock_market.calculate_volume_weighted_stock_price("FIR")
        assert expected_vwap == actual_vwap

    def test_calculate_volume_weighted_stock_price_zero_price(self):
        self.test_stock_market.record_trade("TLX", time.time(), 0, "BUY", 180)
        actual_vwap = self.test_stock_market.calculate_volume_weighted_stock_price("TLX")
        assert actual_vwap == 0

    def test_calculate_gbce_all_share_index(self):
        """Ensure GBCE index is calculated correctly"""
        self.test_stock_market.record_trade("ALE", time.time(), 10, "BUY", 130)
        self.test_stock_market.record_trade("GIN", time.time(), 20, "BUY", 140)
        self.test_stock_market.record_trade("JOE", time.time(), 30, "BUY", 150)

        expected_index = statistics.geometric_mean([130, 140, 150]) # Geometric mean
        actual_index = self.test_stock_market.calculate_gbce_all_share_index()

        assert actual_index == pytest.approx(expected_index, rel=1e-6)

    def test_calculate_gbce_all_share_index_no_trades(self):
        """Ensure GBCE index returns 0 when no trades exist"""
        empty_market = GBCEStockMarket(ExchangeData(), TradeRecorder(300))
        assert empty_market.calculate_gbce_all_share_index() == 0

