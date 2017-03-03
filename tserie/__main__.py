import tserie as tsc

print('''
        Welcome to the example tserie program
        '''
        )

# exxon mobile && crude oil
tickers = ['XOM', 'CL']
year = 2010
print('''
        Fetching data for Exxon Mobile and Crude Oil
        '''
        )
comp = tsc.Pairs(tickers, year)
print('''
        Done!
        '''
        )

# do linear comparison
comp.correlate()

#  chevron, natural gas, we energies
bat = tsc.Batch(['CVX', 'NG', 'WEC'], 2016)
print('''
        Done!
        '''
        )
bat.plot()

print('''
        Complete.
        '''
        )
