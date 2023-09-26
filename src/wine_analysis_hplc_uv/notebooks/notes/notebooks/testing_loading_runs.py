from agilette.agilette_core import Library
from time import perf_counter

from pathlib import Path

time_1 = perf_counter()

selected_runs = [
    "2023-03-07_DEBERTOLI_CS_001.D",
    "2023-02-23_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D",
    "2023-02-23_LOR-RISTRETTO.D",
]

lib = Library(Path("/Users/jonathan/0_jono_data"), runs_to_load=selected_runs)

time_2 = perf_counter()
print(time_2 - time_1)

[
    "2023-03-07_DEBERTOLI_CS_001.D",
    "2023-02-23_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D",
    "2023-02-23_LOR-RISTRETTO.D",
]

print(lib.loaded_runs)
