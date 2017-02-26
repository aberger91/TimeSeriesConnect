#!/usr/bin/env python3
'''
python module for finding connections between time series of financial instruments
'''
__author__ = 'Andrew Berger'

from quandl import get as quandl_get
from seaborn import jointplot, plt
from pandas import DataFrame
import datetime as dt
from .config import *

try:    from pandas_datareader import data as pdr
except: raise ImportTSCError('try: pip install pandas_datareader')


class Frame(object):
    '''
    act like a df if we can else err
    '''
    def __init__(self, product, year):
        self.product =  product
        self.year =     year
        self.frame =    DataFrame()

    def __getattr__(self, value):
        try:
            return getattr(self.frame, value)
        except Exception as e:
            raise TSCError('attribute %s does not exist\n%s' % (
                            value, e))


class Remote(Frame):
    '''
    handle single posts to quandl, yahoo
    '''
    def __init__(self, product, year):
        super().__init__(product, year)
        self.frame =   self._fetch_data()
        self._col =    self._get_column_name()
        self._series = self.frame[self._col]

    def _quandl(self):
        _start = '%s-01-01' % self.year
        try:
            df = quandl_get(QPRODUCT[self.product], start_date=_start)
        except Exception as e:
            raise TSCError('quandl connection failed %s' % e)
        return df

    def _yahoo(self):
        _start = dt.datetime(int(self.year), 1, 1)
        try:
            df = pdr.DataReader(self.product, 'yahoo', start=_start)
        except Exception as e:
            raise TSCError('yahoo connection failed %s' % e)
        return df

    def _fetch_data(self):
        '''
        stream data into df from quandl else yahoo
        return df
        '''
        df = self._quandl() if self._qproduct_exists() else self._yahoo()
        return df

    def _qproduct_exists(self):
        return self.product in QPRODUCT
        
    def _get_column_name(self):
        '''
        raise error unless column from the df matches parameters
        return str
        '''
        for col in COLUMN_NAMES:
            if col in self.frame.columns:
                return col
        raise TSCError('column does not exist in config')


class Batch(Frame):
    def __init__(self, product, year):
        '''
        lookup and fetch list of product codes
        '''
        super().__init__(product, year)
        for ticker in product:
            ts_object = Remote(ticker, year)
            self.frame[ticker] = ts_object._series

    def plot(self):
        self.frame.plot()
        plt.show()

    def candles(self):
        _candles = DataFrame()
        for name, _df in self.frame.items():
            _df.index = map(lambda x: x.timestamp(), _df.index)
            try:
                candles = list(zip(_df.index.values, 
                                   _df.Open, 
                                   _df.High, 
                                   _df.Low, 
                                   _df.Close))
                _candles[name] = candles
            except Exception as e:
                print('''
                        could not convert %s to candles \n %s
                        ''' % (name, e))
                _candles[name] = []

class Pairs(Batch):
    '''
    comparisons between prices and returns for two time series
    '''
    def __init__(self, tickers, year):
        '''
        pull data for tickers and wrap into new df 
        '''
        super().__init__(tickers, year)
        self._ret_df =  self.frame[1:].pct_change()
        self._dfs =     {'price': self.frame, 'returns': self._ret_df}

    def _check_equal_lengths(self):
        '''
        warning if lengths do not match, for calculations
        return None
        '''
        len_xs, len_ys = [len(self.frame[_]._series) for _ in self.product]
        if len_xs != len_ys:
            print('warning: len mismatch: xs:%s ys:%s' % 
                  (len_xs, len_ys))

    def correlate(self):
        '''
        linear regression, correlation on scatterplot w/ two histograms on the side
        return list of seaborn JointGrid objects
        '''
        figs = []
        for name, _df in self._dfs.items():
            figs.append(jointplot(self.product[0],
                                  self.product[1], 
                                  _df._series,
                                  kind='reg', 
                                  annot_kws={'title': name}))
        plt.show()
        return figs
        
    def plot_volatility(self):
        '''
        (annualized) stdev of returns - volatility measure
        return plt
        '''
        for name, _df in self._dfs.items():
            _df._series.dropna() \
                .rolling(250) \
                .std() \
                .plot(title='250 window stdev - %s' % name)
        plt.show()
        return plt
