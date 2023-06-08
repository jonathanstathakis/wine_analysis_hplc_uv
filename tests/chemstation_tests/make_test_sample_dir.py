import os
import random
from glob import glob
import shutil


def create_test_pool(src_dir, dst_parent_dir):
    """
    Create a random sample of .D dirs for testing Chemstation. Provide a parent directory path and list of source sample dirpaths
    """
    print(f"sourcing .D from {src_dir}")
    print(f"destination path: {dst_parent_dir}")

    sample_dirpath_list = get_files_list(src_dir)
    create_test_data_dir(
        dst_parent_dir=dst_parent_dir, sample_dirpath_list=sample_dirpath_list
    )


def get_files_list(src_dir: str) -> list[str]:
    assert os.path.exists(src_dir)
    glob_gen = glob(f"{src_dir}**/*.D", recursive=True)
    glob_list = list(glob_gen)

    sample_size = int(len(glob_list) * 0.05)

    sampled_filepath_list = random.sample(glob_list, sample_size)
    # print(f"sample filepath list: {sampled_filepath_list}")

    assert len(sampled_filepath_list) == sample_size
    assert all(sample in glob_list for sample in sampled_filepath_list)

    return sampled_filepath_list


def create_test_data_dir(dst_parent_dir: str, sample_dirpath_list: list):
    os.makedirs(dst_parent_dir, exist_ok=True)

    for src_dir in sample_dirpath_list:
        src_base_name = os.path.basename(src_dir)
        dst_dir = os.path.join(dst_parent_dir, src_base_name)
        if os.path.exists(dst_dir):
            print(f"dest already exists: {dst_dir}")
            return
        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

    for dir in os.listdir(dst_parent_dir):
        print(os.path.join(dst_parent_dir, dir))

    return None
