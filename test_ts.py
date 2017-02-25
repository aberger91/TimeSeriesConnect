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