"""
This module is to convert agilent .ch to .csv while remaining within the agilent DATA file heirarchy,
adding the .csv files to a "csv_files" subdir in the .D dir.
"""
from pathlib import Path

import rainbow as rb

import re


def signal_converter_to_csv(path: str):

    p = Path(path)

    data_dir_file_path_list = [x for x in p.iterdir() if ".D" in x.name]

    for data_dir_file_path in data_dir_file_path_list:
        print("datadir file path:", data_dir_file_path)

        for datadir in [rb.read(str(data_dir_file_path.resolve()))]:

            try:

                csv_folder_path = data_dir_file_path.joinpath("csv_files")

                if not csv_folder_path.exists():

                    print("folder does not exist, creating {}".format(csv_folder_path))

                    csv_folder_path.mkdir()

                if csv_folder_path.exists():
                    print("{} already exists".format(csv_folder_path))

            except(RuntimeError, TypeError, NameError):
                print("error in creating csv_files directory")

            try:

                for datafile in datadir.datafiles:
                    csv_data_file_name = str(datafile).replace(".ch", ".csv")

                    csv_data_file_name = re.sub("DAD1.", "{}".format(datafile.ylabels[0].replace(".", "_")), csv_data_file_name)

                    csv_datafile_path = data_dir_file_path.joinpath("csv_files", csv_data_file_name)

                    if csv_datafile_path.exists():
                        print("{} already exists".format(csv_datafile_path))

                    if not csv_datafile_path.exists():

                        print("{} created".format(csv_datafile_path))

                        datafile.export_csv(str(csv_datafile_path.resolve()))

            except(RuntimeError, TypeError, NameError):
                print("experienced an error converting the .ch to .csv for {}".format(csv_datafile_path))

            finally:
                print("\n")