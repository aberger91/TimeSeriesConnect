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
        self._start = '%s-01-01' % year
        self.frame =   self._fetch_data()
        self._series = self._get_series()

    def _get_series(self):
        _col =    self._get_column_name()
        _series = self.frame[_col]
        return self._series

    def _fetch_data(self):
        '''
        stream data into df from quandl else yahoo
        return df
        '''
        if self.product in QPRODUCT:
            quandl_code = QPRODUCT[self.product]
            df = quandl_get(quandl_code, start_date=self._start)
        else:
            df = pdr.DataReader(self.product, 'yahoo', start=self._start)
        return df

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
    def __init__(self, products, year):
        '''
        lookup and fetch list of product codes
        '''
        super().__init__(products, year)
        self.frames = dict()
        self.add(products)

    def add(self, products):
        for ticker in products:
            if ticker not in self.product:
                self.product += ticker
            ts_conn = Remote(ticker, self.year)
            self.frames[ticker] = ts_conn

    def __iter__(self):
        for key, conn_obj in self.frames.items():
            yield key, conn_obj

    def __getattr__(self, val):
        '''
        override Frame, handle pd.Series calls
        '''
        try:
            for name, conn_obj in self.frames.items():
                #TODO // return a list of items
                return getattr(conn_obj._series, val)
        except Exception as e:
            pass


class Pairs(Batch):
    '''
    comparisons between prices and returns for two time series
    '''
    def __init__(self, products, year):
        '''
        pull data for products and wrap into new df 
        '''
        super().__init__(products, year)
        self._add_returns_column()
        self._check_equal_lengths()

    def _add_returns_column(self):
        for name, conn_obj in self.frames.items():
            conn_obj._ret_df =  conn_obj._series.pct_change()

    def _check_equal_lengths(self):
        '''
        warning if lengths do not match, for calculations
        return None
        '''
        len_xs, len_ys = [len(self.frames[df]._series) for df in self.frames.keys()]
        if len_xs != len_ys:
            print('warning: len mismatch: xs:%s ys:%s' % 
                  (len_xs, len_ys))

    def correlate(self):
        '''
        linear regression, correlation on scatterplot w/ two histograms on the side
        return list of seaborn JointGrid objects comparing correlations on price vs returns
        '''
        figs = []
        for name, conn_obj in self.frames.items():
            xs, ys = self.product
            dat = DataFrame({xs: self.frames[name]._series,
                             ys: self.frames[name]._ret_df})
            figs.append(jointplot(xs,
                                  ys,
                                  dat,
                                  kind='reg', 
                                  annot_kws={'title': 'prices'}))
        plt.show()
        return figs
        
    def plot_volatility(self):
        '''
        (annualized) stdev of returns - volatility measure
        return plt
        '''
        for name, conn_obj in self.frames.items():
            for attr in ['_series', '_ret_df']:
                getattr(conn_obj, attr).dropna() \
                                       .rolling(250) \
                                       .std() \
                                       .plot(title='250 window stdev prices')
        plt.show()
        return plt
