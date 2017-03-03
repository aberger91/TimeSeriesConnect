'''
simple app that takes input <xs_str, ys_str, start_year>
and does linear regression/correlation and histogram plots
where xs_str and ys_str are exchange product codes or yahoo stock ticker
exchange product codes are identical to product codes on CME, ICE, LIFFE, etc ..
'''
import tserie as tsc
import matplotlib.pyplot as plt
    
xs_str = 'GC'
ys_str = '6J'
start_year = 2015


if __name__ == '__main__':

    #conn = Pairs([xs_str, ys_str], start_year)
    #conn.correlate()

    #bat = Batch(['WEC', 'CL'], 2010)
    #bat.plot()

    rem = tsc.Remote('GC', 2009)

    rem.autocorr()
    mse = rem.autoregress()
    print('Mean Squared Error: %s' % mse)
