'''
simple app that takes input <xs_str, ys_str, start_year>
and does linear regression/correlation and histogram plots
where xs_str and ys_str are exchange product codes or yahoo stock ticker
exchange product codes are identical to product codes on CME, ICE, LIFFE, etc ..
'''
from tserie import Pairs, Batch
        
if __name__ == '__main__':
    from sys import argv
    
    if len(argv) > 3:

        xs_str = argv[1]
        ys_str = argv[2]
        start_year = argv[3]

        conn = Pairs([xs_str, ys_str], start_year)

        conn.correlate()
        conn.plot_volatility()

        bat = Batch(['WEC', 'CL'], 2010)
        print(bat.head()) 

        bat.plot()

    else:
        raise ValueError('usage: ts_connect.py <xs_str> <ys_str> <start_year>')
