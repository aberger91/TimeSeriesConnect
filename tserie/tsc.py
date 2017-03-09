#!/usr/bin/env python3
'''
python module for finding connections between time series of financial instruments
'''
__author__ = 'Andrew Berger'

import matplotlib.pyplot as plt
from pandas.tools.plotting import autocorrelation_plot
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.ar_model import AR
from quandl import get as quandl_get
from seaborn import jointplot, plt
from pandas import DataFrame
import datetime as dt
from .config import *

try:    from pandas_datareader import data as pdr
except: raise ImportTSCError('try: pip install pandas_datareader')


class Frame(object):
    '''
    handle single posts to quandl, yahoo
    '''
    def __init__(self, product, start, end):
        self.product =  product
        self._start = '%s-01-01' % start
        self._end =   '%s-01-01' % end
        self.frame =   self._fetch_data()
        self._series = self._get_series()

    def _fetch_data(self):
        '''
        stream data into df from quandl else yahoo
        return df
        '''
        if self.product in QPRODUCT:
            quandl_code = QPRODUCT[self.product]
            df = quandl_get(quandl_code, start_date=self._start, end_date=self._end)
        else:
            df = pdr.DataReader(self.product, 'yahoo', start=self._start, end=self._end)
        return df

    def _get_series(self):
        _col =    self._get_column_name()
        _series = self.frame[_col]
        return _series

    def _get_column_name(self):
        '''
        raise error unless column from the df matches parameters
        return str
        '''
        for col in COLUMN_NAMES:
            if col in self.frame.columns:
                return col
        raise TSCError('column does not exist in config')

    def autocorr(self):
        autocorrelation_plot(self._series)
        plt.show()

    def autoregress(self, lag=14):
        X = self._series.values
        train, test = X[1:len(X)-lag], X[len(X)-lag:]

        model = AR(train)
        model_fit = model.fit()

        predictions = model_fit.predict(start=len(train),
                                        end=len(train)+len(test)-1,
                                        dynamic=False)
        error = mean_squared_error(test, predictions)

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.plot(test)
        ax.plot(predictions)

        plt.show()
        return error


class Batch(Frame):
    def __init__(self, products, start, end):
        '''
        lookup and fetch list of product codes
        '''
        super().__init__(products, start, end)
        self.frames = dict()
        self.add(products)

    def add(self, products):
        for ticker in products:
            if ticker not in self.product:
                self.product += ticker
            ts_conn = Frame(ticker, self._start, self._end)
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
    def __init__(self, products, start, end):
        '''
        pull data for products and wrap into new df 
        '''
        super().__init__(products, start, end)
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
