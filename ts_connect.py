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
    
class RemoteDataHandler:
    '''
    stream data into df from quandl else yahoo
    '''
    def _quandl(self, product, year):
        _start = '%s-01-01' % year
        try:
            df = quandl_get(QPRODUCT[product], start_date=_start)
        except Exception as e:
            raise TSCError('quandl connection failed %s' % e)
        return df

    def _yahoo(self, product, year):
        _start = dt.datetime(int(year), 1, 1)
        try:
            df = pdr.DataReader(product, 'yahoo', start=_start)
        except Exception as e:
            raise TSCError('yahoo connection failed %s' % e)
        return df

    def _fetch_data(self, product, year):
        #TODO make data structure that replaces logic 
        if self._qproduct_exists(product):
            df = self._quandl(product, year)
        else:
            df = self._yahoo(product, year)
        return df

    def _qproduct_exists(self, product):
        return product in QPRODUCT

        
class DataFetch(RemoteDataHandler):
    def _get_df(self, product):
        '''
        fetch remote data: if not quandl, try yahoo, if not either, raise err
        return df
        '''
        return self._fetch_data(product, self._start_year)
        
    def _col_name(self, cols):
        '''
        raise error unless column from the df matches parameters
        return str
        '''
        for col in COLUMN_NAMES:
            if col in cols:
                return col
        raise TSCError('column does not exist in %s' % COLUMN_NAMES)
        
    def _get_column_names(self):
        '''
        return tuple (of strs) with length 2 or raise err
        '''
        x_col_name = self._col_name(self._xs.columns)
        y_col_name = self._col_name(self._ys.columns)
        return x_col_name, y_col_name
    

class PairComposite(DataFetch):
    '''
    comparisons between prices and returns for two time series
    '''
    def __init__(self, xs, ys, year):
        '''
        pull data for tickers and wrap into new df 
        return df
        '''
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
        self._xs = self._get_df(xs)
        self._ys = self._get_df(ys) 

    def __getattr__(self, value):
        '''
        act like a df if we can
        '''
        if hasattr(self.dfs, value):
            return getattr(self.dfs, value)
        else:
            return getattr(self, value)

    def _init(self):
        col_names = self._get_column_names()
        self._dfs = DataFrame({self._xs_str: self._xs[col_names[0]], 
                               self._ys_str: self._ys[col_names[1]]})
        self._check_equal_lengths()
        self._ret_dfs = self._dfs[1:].pct_change()
        self._data = {'price': self._dfs, 'returns': self._ret_dfs}

    def _check_equal_lengths(self):
        '''
        warning if lengths do not match, for calculations
        return None
        '''
        if len(self._xs) != len(self._ys):
            print('warning: len mismatch: xs:%s ys:%s' % 
                  (len(self._xs), len(self._ys)))

    def correlate(self):
        '''
        linear regression, correlation on scatterplot w/ two histograms on the side
        return list of seaborn JointGrid objects
        '''
        figs = []
        for name, _df in self._data.items():
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
        for name, _df in self._data.items():
            _df.dropna() \
                .rolling(250) \
                .std() \
                .plot(title='250 window stdev - %s' % name)
        plt.show()
        return plt
