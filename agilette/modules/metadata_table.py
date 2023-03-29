import pandas as pd

def metadata_table(self):

        """
        modify this to be applicable to any set of loaded runs in dict form.
        """
                # need to form dicts for each column then combine them together into the DF. Its just gna display the objects of each data object. Q is though, from what list? self.data_file_dir Also I need to find a way to get the acq date without using rainbow.
        
        
        #ids = [idx for idx, x in enumerate(self.all_data_files)]
        #print([x.acq_date for x in list(self.loaded_runs.values())])

        df = pd.DataFrame({
                          "acq_date" : [x.acq_date for x in self.loaded_runs.values()],
                           "sample_name" : [x.name for x in self.loaded_runs.values()],
                           "run_name" : [x.path.name for x in self.loaded_runs.values()],
                           "path" : [x.path for x in self.loaded_runs.values()],
                           "sequence" : [x.sequence_name for x in self.loaded_runs.values()],
                           "ch_files" : [x.data_files_dict['ch_files'] for x in self.loaded_runs.values()],
                           "uv_files" : [x.data_files_dict['uv_files'] for x in self.loaded_runs.values()],
                           "method" : [x.acq_method for x in self.loaded_runs.values()],
                           "desc" : [x.description for x in self.loaded_runs.values()],
                           "run_dir_obj" : [x for x in self.loaded_runs.values()]
                           
        })

        df = df.sort_values('acq_date', ascending = False).reset_index(drop = True)
        