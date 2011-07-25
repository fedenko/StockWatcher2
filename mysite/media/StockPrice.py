class StockPrice:
    def __init__(self, symbol, price, change):
        assert isinstance(symbol, str)
        assert isinstance(price, float)
        assert isinstance(change, float)
        
        self.symbol = symbol
        self.price = price
        self.change = change
    
    def getChangePercent(self):
        return 100.0 * self.change / self.price
