"""

"""
from typing import List
import multiprocessing as mp
from wine_analysis_hplc_uv.etl.build_library.process_chemstation import uv_extractor


def uv_extractor_pool(dirpaths: List[str]) -> tuple:
    """
    Form a multiprocess pool to apply uv_extractor, returning a tuple of dicts for each .D file in the dirpath list.
    """
    global counter, counter_lock
    counter = mp.Value("i", 0)  # 'i' indicates an integer
    counter_lock = mp.Lock()

    def init_pool(counter, lock):
        global counter, counter_lock
        counter = counter
        counter_lock = lock

    print("Initializing multiprocessing pool...\n")
    pool = mp.Pool(initializer=init_pool, initargs=(counter, counter_lock))

    print(f"Processing {len(dirpaths)} directories using a multiprocessing pool...\n")
    uv_file_tuples = pool.map(uv_extractor.uv_extractor, dirpaths)

    print("Closing and joining the multiprocessing pool...\n")
    pool.close()
    pool.join()

    if not isinstance(uv_file_tuples, list):
        print(__file__)
        print(f"uv_file_tuples should be list, but they are {type(uv_file_tuples)}")
        raise TypeError

    print(f"{__file__}\n\nFinished processing files..\n")
    return uv_file_tuples
