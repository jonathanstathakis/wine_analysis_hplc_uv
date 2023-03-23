from pathlib import Path

from agilette.agilette_core import UV_Data

path = next(Path('/Users/jonathan/0_jono_data/').glob("**/*.UV"))

    ## for each run, name the spectrum df the name of the parent directory of the .UV file.
uv_data = UV_Data(path = path)

uv_data = uv_data.extract_uv_data()

print(uv_data.name)