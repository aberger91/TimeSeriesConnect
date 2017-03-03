from tserie import Remote
import argparse

def main():
    import matplotlib.pyplot as plt
    parser = argparse.ArgumentParser()
    parser.add_argument('instrument', nargs=1)
    parser.add_argument('--start', '-s', type=str, required=True)
    parser.add_argument('--lag', '-l', type=str, required=False)
    args = parser.parse_args()
    rem = Remote(*args.instrument, int(args.start))
    mse = rem.autoregress()
    plt.show()
    print('Mean Squared Error: %s' % mse)

if __name__ == '__main__':
    main()
