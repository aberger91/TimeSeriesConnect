#!/usr/bin/env python3
'''
python module for finding connections between time series of financial instruments
'''
__author__ = 'Andrew Berger'

import matplotlib.pyplot as plt
from seaborn import jointplot, pairplot, plt
from pandas.tools.plotting import autocorrelation_plot
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.ar_model import AR
from quandl import get as quandl_get
from pandas import DataFrame
import datetime as dt
from .config import *

try:    from pandas_datareader import data as pdr
except: raise TSCError('try: pip install pandas_datareader')


class ApiStream(object):
    '''
    handle single posts to quandl, yahoo
    '''
    def __init__(self, product, start, end):
        self.product =  product
        self._start =   start
        self._end =     end
        self._frame =   DataFrame
        self._exists =  self._set_frame()
        self._series =  self._extract_series()
        
    def _set_frame(self):
        '''
        stream data into pandas.DataFrame from online
        return df
        '''
        if self.product in QPRODUCT:
            quandl_code = QPRODUCT[self.product]
            self._frame = quandl_get(quandl_code, 
                            start_date=self._start, 
                            end_date=self._end)
        else:
            self._frame = pdr.DataReader(self.product, 
                                'yahoo', 
                                start=self._start, 
                                end=self._end)
        return True if not self._frame.empty else False
        
    def _extract_series(self):
        '''
        raise error unless column from the df matches parameters
        return str
        '''
        for col in COLUMN_NAMES:
            if col in self._frame.columns:
                _series = self._frame[col]
                return _series
        raise TSCError('column does not exist in config')


class TimeSeriesFrame(ApiStream):
    '''
    basic market data instance, supports indexing
    '''
    @property
    def series(self):
        '''
        read-only attribute for user
        '''
        return self._series

    @property
    def exists(self):
        '''
        read-only attribute for user
        '''
        return self._exists

    def __iter__(self):
        '''
        supports for loops
        '''
        if self._exists:
            for row in self._series:
                yield row

    def __getitem__(self, v):
        '''
        access like a sequence
        '''
        if self._exists:
            try:
                item = self._series[v]
                return item
            except Exception as e:
                raise TSCError(e)

    def __str__(self):
        '''
        for printing
        '''
        if self._exists:
            s = str(self._series.head())
            return s
        else:
            s = '%s %s %s' % (self.product, self._start, self._end)
            return s

    def __repr__(self):
        return self.__str__()


class TimeSeriesBatch(object):
    '''
    lookup and fetch list of product codes, start, end
    '''
    def __init__(self, products, start, end):
        '''
        :products   list
        :_start     str
        :_end       str
        '''
        self.products = products
        self._start =   start
        self._end =     end
        self._frames =  dict()
        self.add(products)

    def __iter__(self):
        for key, _frame in self._frames.items():
            yield key, _frame

    def __getattr__(self, val):
        '''
        handle pd.Series calls
        '''
        for name, _frame in self._frames.items():
            try:
                v = getattr(_frame._series, val)
            except Exception as e:
                raise TSCError(e)
        return v

    def add(self, products):
        '''
        insert Frames into _frames
        '''
        for ticker in products:
            if ticker not in self.products:
                self.products += ticker
            _frame = TimeSeriesFrame(ticker, self._start, self._end)
            self._frames[ticker] = _frame

    def lengths(self):
        '''
        return list of lengths of each dataset
        '''
        ret = []
        if self.exists():
            ret = [len(self._frames[df]._series) for df in self._frames.keys()]
        self._min_len = min(ret)
        return ret
    
    def _append_returns_column(self):
        '''
        add attr to each Frame 
        '''
        for name, _frame in self._frames.items():
            _frame._ret_df =  _frame._series.pct_change()
            #TODO // test this:
            #setattr(_frame, '_ret_df', _frame._series.pct_change())

    def _check_equal_lengths(self):
        '''
        warning if lengths do not match, for calculations
        return None
        '''
        lengths = self.lengths()
        if any(map(lambda x: x != lengths[0], lengths)):
            print('''
                    warning: len mismatch
                    ''')
            self._trim_equal_lengths()

    def _trim_equal_lengths(self):
        for name, _frame in self._frames.items():
            _frame = _frame.ix[:self.min_len]

    def pairplot(self):
        pairplot(DataFrame(self._frames), diag_kind="kde")
        plt.show()


class TimeSeriesPairs(TimeSeriesBatch):
    '''
    comparisons between prices and returns for two time series
    '''
    def __init__(self, products, start, end):
        '''
        pull data for products and wrap into new df 
        '''
        super().__init__(products, start, end)
        self._append_returns_column()
        self._check_equal_lengths()

    def correlate(self):
        '''
        linear regression, correlation on scatterplot w/ two histograms on the side
        return list of seaborn JointGrid objects comparing correlations on price vs returns
        '''
        figs = []
        for name, _frame in self._frames.items():
            xs, ys = self.product
            dat = DataFrame({xs: self._frames[name]._series,
                             ys: self._frames[name]._ret_df})
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
        for name, _frame in self._frames.items():
            for attr in ['_series', '_ret_df']:
                getattr(_frame, attr).dropna() \
                                       .rolling(250) \
                                       .std() \
                                       .plot(title='250 window stdev prices')
        plt.show()
        return plt


class AutoRegressions(TimeSeriesFrame):
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
