import argparse

parser = argparse.ArgumentParser(description="test argparser")

parser.add_argument('first arg', metavar = "N", type = int, nargs = '+',
                        help="an integer for the accumulator")
parser.add_argument("--sum", dest = 'accumulate', action = 'store_const',
                        const = sum, default = max,
                        help = 'sum the integers (default: find the max)')

args = parser.parse_args()
print(args.accumulate(args.integers))