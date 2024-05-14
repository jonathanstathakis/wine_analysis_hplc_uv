"""
This module will build a dict of { subdir_name : [children] } for a given root dir. It will use pathlib Paths.

It will also tag each dir with either sequence or single_run to differentiate between the two. That means it will have to be a dict of dict: {file: {metadata : [], children: []}}

Thus each item in the dict can be tested by its metadata. i.e.

[print(x[[children] for x in root_dict if "single_run" in x[metadata])]

It will return the dict of dicts.
"""

from pathlib import Path


def contents_dict():
    p = Path("../002_0_jono_data/")

    # for each item in the root_dir we need to create a dictionary item with {filename : {metdata, data}}

    single_runs = {x for x in p.iterdir() if ".D" in str(x)}

    sequences = [x for x in p.iterdir() if ".D" not in str(x)]

    [print(x) for x in sequences]

    [x.rename(p / "single_runs" / x.name) for x in single_runs]


#    [x.rename(p / "sequences" / x.name) for x in sequences]


#    [print(x.name) for x in p / "single_runs"]
def main():
    contents_dict()


main()
