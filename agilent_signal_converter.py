import argparse

from signal_converter_to_csv import signal_converter_to_csv

parser = argparse.ArgumentParser(description="CLI input to convert .ch files to .csv")

parser.add_argument('--file_path', type = str, nargs = '?', help="provide the file path to the data dir containing the .D dirs."
                        )

args = parser.parse_args(
)

file_path_str = vars(args)["file_path"]

signal_converter_to_csv(file_path_str)