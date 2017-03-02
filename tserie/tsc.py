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
        self._col =    self._get_column_name()
        self._series = self.frame[self._col]

    def _quandl(self):
        try:
            df = quandl_get(QPRODUCT[self.product], start_date=self._start)
        except Exception as e:
            raise TSCError('quandl connection failed %s' % e)
        return df

    def _yahoo(self):
        try:
            df = pdr.DataReader(self.product, 'yahoo', start=self._start)
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
        self.frames = dict()
        self._init_frames()

    def _init_frames(self):
        for ticker in self.product:
            ts_conn = Remote(ticker, self.year)
            self.frames[ticker] = ts_conn

    def __iter__(self):
        for key, conn_obj in self.frames.items():
            yield key, conn_obj

    def __getattr__(self, val):
        '''
        override Frame .. handle pd.Series calls
        '''
        try:
            for name, conn_obj in self.frames.items():
                return getattr(conn_obj._series, val)
        except Exception as e:
            pass

    def plot(self):
        for name, conn_obj in self.frames.items():
            conn_obj._series.plot()
        plt.show()


class Pairs(Batch):
    '''
    comparisons between prices and returns for two time series
    '''
    def __init__(self, product, year):
        '''
        pull data for product and wrap into new df 
        '''
        super().__init__(product, year)
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
        len_xs, len_ys = [len(self.frames[_]._series) for _ in self.product]
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
            dat = DataFrame({xs: self.frames[name]._series, ys: self.frames[name]._ret_df})
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
