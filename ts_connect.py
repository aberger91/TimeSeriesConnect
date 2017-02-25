#!/usr/bin/env python3
'''
python module for finding connections between time series of financial instruments
'''

from seaborn import jointplot, plt
from pandas import DataFrame
import datetime as dt
from quandl import get as quandl_get
from qproducts import QPRODUCT

try:    from pandas_datareader import data as pdr
except: raise ImportError('try: pip install pandas_datareader')

COLUMN_NAMES = ('Adj Close', 'Settle', 'Value', 'Last')

class TSCError(Exception):
    pass
    

class RemoteDataHandler(object):
    '''
    handle posts to quandl, yahoo
    '''
    def __init__(self, product, year):
        self.product = product
        self.year = year

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
        

class TSObject(RemoteDataHandler):
    '''
    proxy for url request handler
    '''
    def __init__(self, product, year):
        '''
        fetch remote data: if not quandl, try yahoo, if not either, raise err
        return df
        '''
        super().__init__(product, year)
        self._df = self._fetch_data()
        self._col = self._extract_col_name(self._df.columns)        
        self._series = self._df[self._col]

    def _extract_col_name(self, cols):
        '''
        raise error unless column from the df matches parameters
        return str
        '''
        for col in COLUMN_NAMES:
            if col in cols:
                return col
        raise TSCError('column does not exist in config')
        
    def __getattr__(self, value):
        '''
        act like a df if we can
        '''
        if hasattr(self._df, value):
            return getattr(self._df, value)
        else:
            return getattr(self, value)


class TSBatch(object):
    def __init__(self, tickers, year):
        '''
        lookup and fetch list of product codes
        '''
        self.tickers = tickers
        self.start_year = year
        self.dfs = (tickers, year)

    @property
    def dfs(self):
        return self._dfs

    @dfs.setter
    def dfs(self, values):
        tickers, year = values
        self._dfs = DataFrame()
        for ticker in tickers:
            ts_object = TSObject(ticker, year)
            self._dfs[ticker] = ts_object._series

    def __getattr__(self, value):
        '''
        act like a df if we can
        '''
        if hasattr(self._dfs, value):
            return getattr(self._dfs, value)
        else:
            return getattr(self, value)

    def plot(self):
        self.dfs.plot()
        plt.show()


class PairComposite(object):
    '''
    comparisons between prices and returns for two time series
    '''
    def __init__(self, tickers, year):
        '''
        pull data for tickers and wrap into new df 
        return df
        '''
        xs, ys = tickers
        self._xs_str =      xs  # product code or stock symbol
        self._ys_str =      ys  # product code or stock symbol
        self._start_year =  year
        self.dfs =          (xs, ys)  # delegate to setter by default
        self._init()

    @property
    def dfs(self):
        return self._dfs

    @dfs.setter
    def dfs(self, values):
        #TODO protect this against err
        xs, ys = values
        self._xs = TSObject(xs, self._start_year)
        self._ys = TSObject(ys, self._start_year)

    def _init(self):
        _xs_series = self._xs._df[self._xs._col]
        _ys_series = self._ys._df[self._ys._col]
        self._dfs = DataFrame({self._xs_str: _xs_series, self._ys_str: _ys_series})
        self._ret_dfs = self._dfs[1:].pct_change()
        self._check_equal_lengths()
        self.__data = {'price': self._dfs, 'returns': self._ret_dfs}

    def _check_equal_lengths(self):
        '''
        warning if lengths do not match, for calculations
        return None
        '''
        if len(self._xs._df) != len(self._ys._df):
            print('warning: len mismatch: xs:%s ys:%s' % 
                  (len(self._xs._df), len(self._ys._df)))

    def correlate(self):
        '''
        linear regression, correlation on scatterplot w/ two histograms on the side
        return list of seaborn JointGrid objects
        '''
        figs = []
        for name, _df in self.__data.items():
            figs.append(jointplot(self._xs_str, 
                                  self._ys_str, 
                                  _df, 
                                  kind='reg', 
                                  annot_kws={'title': name}))
        plt.show()
        return figs
        
    def plot_volatility(self):
        '''
        (annualized) stdev of returns - volatility measure
        return plt
        '''
        for name, _df in self.__data.items():
            _df.dropna() \
                .rolling(250) \
                .std() \
                .plot(title='250 window stdev - %s' % name)
        plt.show()
        return plt

