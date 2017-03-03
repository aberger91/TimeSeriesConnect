from tserie import Pairs
import argparse


def main():
    import matplotlib.pyplot as plt
    parser = argparse.ArgumentParser()
    parser.add_argument('instruments', nargs=2)
    parser.add_argument('--start', '-s', type=str, required=True)
    args = parser.parse_args()
    rem = Pairs(args.instruments, int(args.start))
    rem.correlate()
    plt.show()


if __name__ == '__main__':
    main()
