import tserie as tsc
import argparse

def arguments():
    parser = argparse.ArgumnetParser()
    parser.add_argument('-t', '--ticker',
                        nargs=1,
                        required=True)
    parser.add_argument('-s', '--start',
                        nargs=1,
                        required=True)
    parser.add_argument('-e', '--end',
                        nargs=1,
                        required=True)
    args = parser.parse_args()
    return args.ticker, args.start, args.end

def main():
    ticker, start, end = arguments()

    dat = tsc.Frame(ticker, start, end)
    dat._series.plot()


if __name__ == '__main__':
    main()
