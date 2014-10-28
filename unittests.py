from nasdaq import *
from nose import with_setup
from nose.tools import *

def iteration_counter():
    counter = 0
    qqq = Nasdaq(callback=callback_parser, sleep=0)
    qqq.add_symbol('qqq')

def callback_parser(html):
    if counter>1:
        raise StopIteration('done')
    return '10/28/2014 1:00:00 PM', 100.

@with_setup(iteration_counter)
def test_run():
    assert callback_parser('') == qqq.request() 


