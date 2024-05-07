import sys

import os

# adds root dir 'wine_analyis_hplc_uv' to path.

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from agilette import agilette_core as ag

ag = ag.Agilette("/Users/jonathan/0_jono_data")

acetone_sequence = ag.data_file_dir.sequence_dict[
    "2023-03-01_15-22-02_ACETONE_VOID-VOL-MEASUREMENT.sequence"
]

acetone_0002 = acetone_sequence.data_dict["acetone0002"]

print(acetone_0002.detector_name_to_nm())

#
# print(sorted(acetone_data['acetone0001']))
# class Void_Vol_Measurement:
#     def __init__(self, run_name, injection_vol, data):
#         self.run_name = run_name
#         self.inj_vol = injection_vol
#         self.data = data

#     def __str__(self):
#             return f"run name: {self.run_name}\n inj_vol: {self.inj_vol}\n data: {self.data.head()}"

# inj_vol = {
#     "1_acetone" : 10,
#     "2_acetone" : 8,
#     "3_acetone" : 6,
#     "4_acetone" : 4,
#     "5_acetone" : 2,
#     "6_acetone" : 1
# }

# run_vol_zip = zip(acetone_data.keys(), inj_vol.values())

# void_vol_measure_obj_list = []

# for run, injvol in run_vol_zip:
#     void_vol_measure_obj_list.append(Void_Vol_Measurement(run, inj_vol, acetone_data[run]))

# print(void_vol_measure_obj_list[0])
