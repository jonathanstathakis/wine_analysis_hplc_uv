from agilette.modules.run_dir import Run_Dir

class Sequence:
    """
    Currently just going to contain the data files.

    todo: add start dates.
    """
    def __init__(self, path: str):
        self.path = path
        self.data_files = self.data_files()

    def data_files(self):
        
        try:
            data_file_dict = {Run_Dir(x).name : Run_Dir(x) for x in self.path.iterdir() if x.name.endswith(".D")}
                    
        except Exception as e:
            print(f"{e}")
        
        return data_file_dict
        
    def __str__(self):
        return f"{self.path.name}, {self.data_files.keys()}"