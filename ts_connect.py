#!/usr/bin/env python3
'''
python module for finding connections between time series of financial instruments

daily linear correlation between daily E-Mini S&P and Euro/USD futures example:
python test_ts.py 6E ^GSPC 2012
'''

from seaborn import jointplot, plt
from pandas import DataFrame
import datetime as dt
from quandl import get as quandl_get
from qproducts import FUTURES

try:    from pandas_datareader import data as pdr
except: raise ImportError('try: pip install pandas_datareader')

class Params:
    '''
    global, read-only variables chosen before running program
    '''
    def __init__(self):
        self.QPRODUCTS =    self.QPRODUCTS
        self.VIEWS =        self.VIEWS
        self.COLUMN_NAMES = self.COLUMN_NAMES
    
    @property
    def QPRODUCTS(self):
        '''
        mapping of exchange product codes to quandl urls
        '''
        return FUTURES
        
    @property
    def VIEWS(self):
        '''
        mapping of source to (function, start, kwargs)
        '''
        return {'quandl':
                    {'f':      quandl_get,
                     '_start': '%s-01-01', 
                     '_kwarg': 'start'}, 
                'yahoo': 
                    {'f':      pdr.DataReader, 
                     '_start': dt.datetime(int(year), 1, 1), 
                     '_kwarg': 'start_date'}
               }
        
    @property
    def COLUMN_NAMES(self):
        '''
        known column names to perform calculations on
        '''
        return ('Adj Close', 'Settle', 'Value', 'Last')
    
class TSDataHandler(Params):
    '''
    stream data into df from quandl else yahoo
    '''
    def _fetch_data(self, product, year):
        #TODO make data structure that replaces logic 
        if self._qproduct_exists(product):
            _start = '%s-01-01' % year
            try:
                df = quandl_get(self.QPRODUCTS[product], start_date=_start)
            except Exception as e:
                raise ValueError('quandl connection failed %s' % e)
            
        else:  # try yahoo
            _start = dt.datetime(int(year), 1, 1)
            try:
                df = pdr.DataReader(product, 'yahoo', start=_start)
            except Exception as e:
                raise ValueError('yahoo connection failed %s' % e)
                
        return df

    def _qproduct_exists(self, product):
        return product in self.QPRODUCTS

        
class TSConnections(TSDataHandler):
    def __init__(self, xs, ys, year):
        self._xs_str = xs  # product code or stock symbol
        self._ys_str = ys  # product code or stock symbol
        self.start_year = year  # int
        
        self.xs, self.ys = self._get_df(xs), self._get_df(ys) 
        x_col, y_col = self._get_column_names()
        
        self.dfs = DataFrame({xs: self.xs[x_col], ys: self.ys[y_col]})
        self._do_calculations()
        self.data = {'price': self.dfs, 'returns': self.ret_dfs}
        
    def _do_calculations(self):
        '''
        prelim calculations
        return None
        '''
        self.check_equal_lengths()
        self.ret_dfs = self.dfs[1:].pct_change()
        
    def _get_df(self, product):
        '''
        fetch remote data
        if not quandl, try yahoo, if not either, raise err
        return df
        '''
        return self._fetch_data(product, self.start_year)
        
    def _col_name(self, cols):
        '''
        raise error unless a column from the df matches
        return str
        '''
        for col in self.COLUMN_NAMES:
            if col in cols:
                return col
        raise ValueError('column does not exist in %s' % self.COLUMN_NAMES)
        
    def _get_column_names(self):
        '''
        return tuple (of strs) with length 2 or raise err
        '''
        x_col, y_col = self._col_name(self.xs.columns), self._col_name(self.ys.columns)
        return x_col, y_col
    
    def do_correlation(self):
        '''
        linear regression, correlation on scatterplot w/ two histograms on the side
        return list
        '''
        figs = []
        for name, _df in self.data.items():
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
        for name, _df in self.data.items():
            _df.dropna() \
                .rolling(250) \
                .std() \
                .plot(title='250 window stdev - %s' % name)
        plt.show()
        return plt
        
    def check_equal_lengths(self):
        '''
        warning if lengths do not match
        return None
        '''
        if len(self.xs) != len(self.ys):
            print('warning: len mismatch: xs:%s ys:%s' % 
                  (len(self.xs), len(self.ys)))
