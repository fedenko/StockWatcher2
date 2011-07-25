#import pyjd

from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.FlexTable import FlexTable
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.TextBox import TextBox
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.KeyboardListener import KeyboardHandler, KEY_ENTER
from pyjamas.Timer import Timer
from pyjamas import Window
from pyjamas.Cookies import getCookie

from pyjamas.JSONService import JSONProxy

from StockPrice import StockPrice

import re
import random
import datetime

class StockWatcher:
    def onModuleLoad(self):
        '''
        This is the main entry point method.
        '''
        
        # Setup JSON RPC
        self.remote = DataService()
        
        # Initialize member variables
        self.mainPanel = VerticalPanel()
        self.stocksFlexTable = FlexTable()
        self.addPanel = HorizontalPanel()
        self.newSymbolTextBox = TextBox()
        self.lastUpdatedLabel = Label()
        self.addStockButton = Button('Add', self.addStock)
        self.stocks = []
        self.stocksTableColumns = ['Symbol', 'Price', 'Change', 'Remove']
        
        # Add styles to elements in the stock list table
        self.stocksFlexTable.getRowFormatter().addStyleName(0, 'watchListHeader')
        self.stocksFlexTable.addStyleName('watchList')
        self.stocksFlexTable.getCellFormatter().addStyleName(0, 1, 'watchListNumericColumn')
        self.stocksFlexTable.getCellFormatter().addStyleName(0, 2, 'watchListNumericColumn')
        self.stocksFlexTable.getCellFormatter().addStyleName(0, 3, 'watchListRemoveColumn')
        
        # Create table for stock data
        for i in range(len(self.stocksTableColumns)):
            self.stocksFlexTable.setText(0, i, self.stocksTableColumns[i])
        
        # Assemble Add Stock panel
        self.addPanel.add(self.newSymbolTextBox)
        self.addPanel.add(self.addStockButton)
        self.addPanel.addStyleName('addPanel')
        
        # Assemble Main panel
        self.mainPanel.add(self.stocksFlexTable)
        self.mainPanel.add(self.addPanel)
        self.mainPanel.add(self.lastUpdatedLabel)
        
        # Associate the Main panel with the HTML host page
        RootPanel().add(self.mainPanel)
        
        # Move cursor focus to the input box
        self.newSymbolTextBox.setFocus(True)
        
        # Setup timer to refresh list automatically
        refresh = self.refreshWatchlist
        class MyTimer(Timer):
            def run(self):
                refresh()
        refreshTimer = MyTimer()
        refreshTimer.scheduleRepeating(5000)
        
        # Listen for keyboard events in the input box
        self_addStock = self.addStock
        class StockTextBox_KeyboardHandler():
            def onKeyPress(self, sender, keycode, modifiers):
                if keycode == KEY_ENTER:
                    self_addStock()
            def onKeyDown(self, sender, keycode, modifiers): return
            def onKeyUp(self, sender, keycode, modifiers): return
        self.newSymbolTextBox.addKeyboardListener(StockTextBox_KeyboardHandler())
        
        # Load the stocks
        self.remote.getStocks(self)
    
    def addStock(self, sender, symbol=None):
        '''
        Add stock to FlexTable. Executed when the user clicks the addStockButton
        or presses enter in the newSymbolTextBox
        '''
        
        if symbol is None:
            # Get the symbol
            symbol = self.newSymbolTextBox.getText().upper().trim()
            self.newSymbolTextBox.setText('')
            # Don't add the stock if it's already in the table
            if symbol in self.stocks:
                return
            # Tell the server that we're adding this stock
            self.remote.addStock(symbol, self)
            self.newSymbolTextBox.setFocus(True)
            # Stocks code must be between 1 and 10 chars that are numbers/letters/dots
            p = re.compile('^[0-9A-Z\\.]{1,10}$')
            if p.match(symbol) == None:
                Window.alert('"%s" is not a valid symbol.' % symbol)
                self.newSymbolTextBox.selectAll()
                return    
        
        # Add the stock to the table
        row = self.stocksFlexTable.getRowCount()
        self.stocks.append(symbol)
        self.stocksFlexTable.setText(row, 0, symbol)
        self.stocksFlexTable.setWidget(row, 2, Label())
        self.stocksFlexTable.getCellFormatter().addStyleName(row, 1, 'watchListNumericColumn')
        self.stocksFlexTable.getCellFormatter().addStyleName(row, 2, 'watchListNumericColumn')
        self.stocksFlexTable.getCellFormatter().addStyleName(row, 3, 'watchListRemoveColumn')
        
        # Add a button to remove this stock from the table
        def _removeStockButton_Click(event):
            if symbol not in self.stocks:
                return
            removedIndex = self.stocks.index(symbol)
            self.remote.deleteStock(symbol, self)
            self.stocks.remove(symbol)
            self.stocksFlexTable.removeRow(removedIndex + 1)
        removeStockButton = Button('x', _removeStockButton_Click)
        removeStockButton.addStyleDependentName('remove')
        self.stocksFlexTable.setWidget(row, 3, removeStockButton)
        
        # Get the stock price
        self.refreshWatchlist()
    
    def refreshWatchlist(self):
        '''
        Update the price change for each stock
        '''
        
        MAX_PRICE = 100.0
        MAX_PRICE_CHANGE = 0.02
        
        prices = []
        for i in range(len(self.stocks)):
            price = random.random() * MAX_PRICE
            change = price * MAX_PRICE_CHANGE * (random.random() * 2.0 - 1.0)
            prices.append(StockPrice(self.stocks[i], price, change))
        
        self.updateTable(prices)
    
    def updateTable(self, prices):
        '''
        Update the price and change fields of all the rows in the stock table
        
        prices -- List of StockPrice objects for all rows
        '''
        
        # Type checking
        assert isinstance(prices, list)
        for price in prices:
            assert isinstance(price, StockPrice)
        
        # Nothing to do...
        if len(prices) == 0:
            return
        
        # Update each individual row
        for i in range(len(prices)):
            self.updateRow(prices[i])
        
        # Display timestamp showing last refresh
        self.lastUpdatedLabel.setText("Last update: %s" % datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S %p"))
    
    def updateRow(self, price):
        '''
        Update a single row in the stock table
        
        price -- StockPrice object for a single row
        '''
        
        # Type checking
        assert isinstance(price, StockPrice)
        
        # Make sure the stock is still in the stock table
        if price.symbol not in self.stocks:
            return
        
        # Find the index of 
        row = self.stocks.index(price.symbol) + 1
        
        # Populate the price and change fields with new data
        self.stocksFlexTable.setText(row, 1, '%.2f' % price.price)
        changeWidget = self.stocksFlexTable.getWidget(row, 2)
        changeWidget.setText('%.2f (%.2f%%)' % (price.change, price.getChangePercent()))
        
        # Change the color of the text in the Change field based on its value
        changeStyleName = 'noChange'
        if price.getChangePercent() < -0.1:
            changeStyleName = 'negativeChange'
        else:
            changeStyleName = 'positiveChange'
        
        changeWidget.setStyleName(changeStyleName)
    
    def onRemoteResponse(self, response, request_info):
        '''
        Called when a response is received from a RPC.
        '''
        if request_info.method in DataService.methods:
            # Compare self.stocks and the stocks in response
            stocks_set = set(self.stocks)
            response_set = set(response)
            # Add the differences
            for symbol in list(response_set.difference(stocks_set)):
                self.addStock(None, symbol)
        else:
            Window.alert('Unrecognized JSONRPC method.')
            
    def onRemoteError(self, code, message, request_info):
        Window.alert(message)
        #print code, message, resp_info 

class DataService(JSONProxy):
    methods = ['getStocks', 'addStock', 'deleteStock']
    
    def __init__(self):
        JSONProxy.__init__(self, 'services/', DataService.methods, {'X-CSRFToken': getCookie('csrftoken')})

if __name__ == '__main__':
    #pyjd.setup('./StockWatcher.html')
    app = StockWatcher()
    app.onModuleLoad()
    #pyjd.run()

