import matplotlib.pyplot as plt
import tserie as tsc
import argparse

def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('ticker', nargs=1)
    parser.add_argument('start', nargs=1)
    parser.add_argument('end', nargs=1)
    args = parser.parse_args()
    return args.ticker, args.start, args.end

def main():
    ticker, start, end = arguments()
    dat = tsc.TimeSeriesBatch(ticker, start, end)
    dat.plot()
    plt.show()

if __name__ == '__main__':
    main()
