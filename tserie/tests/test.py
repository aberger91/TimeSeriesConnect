'''
simple app that takes input <xs_str, ys_str, start_year>
and does linear regression/correlation and histogram plots
where xs_str and ys_str are exchange product codes or yahoo stock ticker
exchange product codes are identical to product codes on CME, ICE, LIFFE, etc ..
'''
from tsc import TSCPairs, TSCBatch
        
if __name__ == '__main__':
    from sys import argv
    
    if len(argv) > 3:

        xs_str = argv[1]
        ys_str = argv[2]
        start_year = argv[3]

        conn = TSCPairs([xs_str, ys_str], start_year)

        conn.correlate()
        conn.plot_volatility()

        bat = TSCBatch(['WEC', 'XLE', 'XOM', 'CVX', 'NG', 'CL'], 2010)
        print(bat.head()) 

    else:
        raise ValueError('usage: ts_connect.py <xs_str> <ys_str> <start_year>')