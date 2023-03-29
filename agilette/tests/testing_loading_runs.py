from agilette.modules.library import Library
from pathlib import Path

def testing_library() -> None:

    # path = Path('/Users/jonathan/0_jono_data/2023-02-23_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D')

    path = [
            '/Users/jonathan/0_jono_data/2023-02-23_2021-DEBORTOLI-CABERNET-MERLOT_AVANTOR.D',
            '/Users/jonathan/0_jono_data/2023-02-22_KOERNER-NELLUCIO-02-21.D',
            '/Users/jonathan/0_jono_data/2023-02-16_0291.D'
            ]

    lib = Library(path)

    loaded_spectrums = lib.load_spectrum()
    loaded_spectrums['spectrum_obj'].apply(lambda x : x.line_plot())

testing_library()