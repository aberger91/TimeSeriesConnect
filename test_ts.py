'''
simple app that takes input <xs, ys, year>
and does linear regression/correlation and histogram plots
where xs and ys are exchange product codes or yahoo stock ticker
exchange product codes are identical to product codes on CME, ICE, LIFFE, etc ..
'''
from ts_connect import TSConnections
        
if __name__ == '__main__':
    from sys import argv
    
    if len(argv) > 3:
        xs = argv[1]
        ys = argv[2]
        year = argv[3]
    else:
        raise ValueError('usage: ts_connect.py <xs> <ys> <year>')
        
    conn = TSConnections(xs, ys, year)
    
    conn.do_correlation()
    conn.plot_volatility()
