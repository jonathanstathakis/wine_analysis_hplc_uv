import os

def dir_ext_set_dict_builder(path, dir_list):

    ext_set_dict = {}

    for obj in dir_list:

        # form filepath objects combined from the root path and each element of
        # the iterated list

        # this level is the objects at root.

        file_path = os.path.join(path, obj)
        
        if os.path.isdir(file_path):

            sub_dir_list = os.listdir(file_path)
        

            sub_obj_ext_set = set()

            for sub_obj in sub_dir_list:
                # this is iterating through subdirs too.

                sub_obj_ext = sub_obj.split(".")[1]

                sub_obj_ext_set.add(sub_obj_ext)

        ext_set_dict[obj] = sub_obj_ext_set
        
    return ext_set_dict

def main():
    
    path = "/Users/jonathan/002_0_jono_data"
                                 
    ext_set_dict = dir_ext_set_dict_builder(path, os.listdir(path))
    
    for pair in ext_set_dict.items():
        print(pair)

main()