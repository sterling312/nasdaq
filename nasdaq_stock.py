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
    tickers = set()
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
        if isinstance(ticker, (str, unicode)):
            self.tickers.add(ticker)
        if isinstance(ticker, list):
            for i in ticker:
                self.tickers.add(i)

    def request(self):
        for ticker in self.tickers:
            path = self.real_time_path.format(ticker)
            req = self.sess.get(urlparse.urljoin(self.base_url, path))
            if req.ok:
                try:
                    price = self.parse(req.text)
                    self.callback(json.dumps(price))
                except Exception as e:
                    logging.error(e)
            else:
                logging.error(req.reason)

    def run(self):
        while True:
            self.request()
            time.sleep(self.sleep)

if __name__=='__main__':
    args = parser.parse_args()
    ndq = Nasdaq(sleep=args.sleep)
    ndq.subscribe(args.ticker.split(','))
    ndq.run()
