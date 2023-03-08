# A snippet to remove any 'empty' sequences from the data directory. Good for initial data cleaning.

from pathlib import Path

import shutil

p = Path('/Users/jonathan/0_jono_data')

for direc in p.iterdir():
    try:
        if direc.exists():
            if not direc.is_dir():  # Skip non-directory files
                continue
            if not direc.name.endswith(".sequence"):  # Skip directories that don't end with ".sequence"
                continue
            if not any(direc.glob("*.D")):  # Check if there are any files with ".D" extension in the directory
                print(f"Deleting directory {direc}")
                shutil.rmtree(direc)
                direc.rmdir()  # Remove the directory if there are no ".D" files
    except Exception as e:
        print(e)