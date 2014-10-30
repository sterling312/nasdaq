#!/usr/bin/env python
try:
    from urllib2 import urlparse
    urljoin = urlparse.urljoin
except ImportError:
    from urllib.parse import urljoin
import sys
import json
import logging
import datetime
import time
import array
import requests
from pyquery import PyQuery

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')

class Tick(array.array):
    max_tick = 20
    def add(self, value):
        if len(self) >= self.max_tick: 
            self.pop(0)
        self.append(value)

def pyquery_parser(html):
    error = None
    html = PyQuery(html)
    p = html.find('div.qwidget-dollar').eq(0)
    price = p.text().lstrip('$')
    if not price.replace('.','').isdigit():
        raise TypeError('price is not numeric')
    price = float(price)
    timestamp = p.parent().next().find('span').text()
    if len(timestamp)==10:
        timestamp = datetime.datetime.strptime(timestamp, '%m/%d/%Y')
        raise StopIteration('market closed')
    else:
        timestamp = datetime.datetime.strptime(timestamp, '%m/%d/%Y %I:%M:%S %p')
    return timestamp, price

class Nasdaq(object):
    base_url = 'http://www.nasdaq.com'
    ticks = {}
    def __init__(self, callback=pyquery_parser, sleep=1, logger=None):
        self.callback = callback
        self.sleep = sleep
        self.result = {}
        if logger is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
        self.logger = logger

    def add_symbol(self, symbol):
        if symbol not in self.ticks:
            self.ticks[symbol] = Tick('d')

    def request(self, result=False):
        real_time = 'symbol/{}/real-time'
        for symbol, tick in self.ticks.items():
            url = urljoin(self.base_url, real_time.format(symbol))
            req = requests.get(url)
            if not req.ok:
                self.logger.error(req.reason)
                return False
            try:
                timestamp, price = self.callback(req.text)
                if result:
                    self.result[symbol] = price
            except Exception as e:
                self.logger.error(str(e))
                return False
            self.logger.info('timestamp: {}, symbol: {}, price: {}'.format(timestamp,symbol,price))
            tick.add(price)
        return True

    def run(self):
        while self.request():
            time.sleep(self.sleep)

    def stream_price(self):
        while self.request(result=True):
            yield self.result
            time.sleep(self.sleep)

    def to_websocket(self):
        while self.request(result=True):
            msg = json.dumps(self.result)
            time.sleep(self.sleep)

if __name__=='__main__':
    qqq = Nasdaq(sleep=0)
    for symbol in sys.argv[1:]:
        qqq.add_symbol(symbol)
    qqq.run()
