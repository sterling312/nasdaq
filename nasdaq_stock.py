#!/usr/bin/env python
from __future__ import print_function
import argparse
import json
import logging
import datetime
import time
import requests
from urllib2 import urlparse
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--ticker', required=True, help='comma separated ticker to view')
parser.add_argument('-s', '--sleep', type=int, default=0, help='sleep time between intervals')

class Nasdaq(object):
    base_url = 'http://www.nasdaq.com'
    real_time_path = 'symbol/{}/real-time'
    tickers = {}
    def __init__(self, callback=print, sleep=0):
        self.sleep = sleep
        self.sess = requests.session()
        self.callback = callback

    @staticmethod
    def parse(html):
        bs = BeautifulSoup(html)
        p = bs.find('div', class_='qwidget-dollar')
        price = p.text
        if not price or not price.lstrip('$').replace('.', '').isdigit():
            raise ValueError('price is not numeric')
        price = float(price.lstrip('$'))
        return price

    def subscribe(self, ticker):
        if ticker in self.tickers:
            self.tickers[ticker] += 1
        else:
            self.tickers[ticker] = 1
        logging.debug('{} subscribed to {}'.format(self.tickers[ticker], ticker))

    def unsubscribe(self, ticker):
        if ticker in self.tickers:
            self.tickers[ticker] -= 1
        logging.debug('{} subscribed to {}'.format(self.tickers[ticker], ticker))

    def add_ticker(self, ticker):
        if isinstance(ticker, (str, unicode)):
            self.subscribe(ticker)
        elif isinstance(ticker, list):
            for i in ticker:
                self.subscribe(i)

    def remove_ticker(self, ticker):
        if isinstance(ticker, (str, unicode)):
            self.unsubscribe(ticker)
        elif isinstance(ticker, list):
            for i in ticker:
                self.unsubscribe(i)

    def request(self):
        for ticker, i in self.tickers.items():
            if i:
                path = self.real_time_path.format(ticker.lower())
                req = self.sess.get(urlparse.urljoin(self.base_url, path))
                if req.ok:
                    try:
                        price = self.parse(req.text)
                        self.callback(json.dumps({ticker.upper(): price}))
                        yield {ticker: price}
                    except Exception as e:
                        logging.error(e)
                        del self.tickers[ticker]
                else:
                    logging.error(req.reason)
            else:
                del self.tickers[ticker]

    def run(self):
        while True:
            for price in self.request():
                continue
            time.sleep(self.sleep)

if __name__=='__main__':
    args = parser.parse_args()
    ndq = Nasdaq(sleep=args.sleep)
    ndq.add_ticker(args.ticker.split(','))
    ndq.run()
