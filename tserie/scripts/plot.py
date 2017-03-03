from tserie import Batch
import argparse

def main():
    import matplotlib.pyplot as plt
    parser = argparse.ArgumentParser()
    parser.add_argument('--instruments', '-i', type=str, required=True)
    parser.add_argument('--start', '-s', type=str, required=True)
    args = parser.parse_args()
    rem = Batch(args.instruments.split(), int(args.start))
    rem.plot()
    plt.show()

if __name__ == '__main__':
    main()
