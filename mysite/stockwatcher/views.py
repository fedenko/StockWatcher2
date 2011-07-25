from stockwatcher.network import *
#from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.sessions.models import Session

from stockwatcher.models import Stocks

import datetime

service = JSONRPCService()

#@ensure_csrf_cookie    
def index(request):
    request.session.set_expiry(datetime.datetime.now() + datetime.timedelta(365))
    request.session.save()
    get_token(request)
    return render_to_response('StockWatcher.html')
  
@jsonremote(service)
def getStocks(request):
    try:
        session = Session.objects.get(pk=request.session._session_key)
        stocks = Stocks.objects.filter(session=session)
    except Exception as e:
        return []
    return [(stock.symbol) for stock in stocks]
    
@jsonremote(service)
def addStock(request, symbol):
    session = Session.objects.get(pk=request.session._session_key)
    # Don't allow duplicates
    if len(Stocks.objects.filter(session=session, symbol=symbol)) > 0:
        return getStocks(request)
    stock = Stocks()
    stock.session = session
    stock.symbol = symbol
    stock.save()
    return getStocks(request)

@jsonremote(service)
def deleteStock(request, symbol):
    try:
        session = Session.objects.get(pk=request.session._session_key)
        Stocks.objects.get(session=session, symbol=symbol).delete()
    except Stocks.DoesNotExist:
        pass
    return getStocks(request)

