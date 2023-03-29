from bs4 import BeautifulSoup
import rainbow as rb
from datetime import datetime
from pathlib import Path

from scripts.acaml_read import signal_metadata

from agilette.modules.agilette_core import Single_Signal, UV_Data

class Run_Dir:
    """
    A single run directory containing signal data and metadata about the run.

    Use extract_uv_data(self) to get the Spectrum.

    To get ch data, it is useful to view each signal's wavelength and band rather than the detector name, so run self.extract_ch_data() to get a dictionary of each signal with its wavelength as the key and dataframe of the signal as value.
    """
    def __init__(self, path: Path):
        self.path = path
        self.name, self.description, self.acq_method = self.load_meta_data()
        self.acq_date = self.get_acq_datetime()
        self.sequence_name = self.sequence_name()

        self.data_files_dict = self.data_files_dicter()

        self.single_signals_metadata, self.spectrum_metadata = self.get_signal_metadata()
        self.spectrum = None
        self.metadata = self.load_meta_data()

    def get_signal_metadata(self):
        return signal_metadata(self.path)

    def metadata_to_list(self):
        """
        Retruns a list metadata objects for use in `Library.get_metadata_list()`
        """
        return [self.acq_date, 
                self.name, 
                self.path,
                self.acq_method,
                self.description,
                self.sequence_name,
                self.data_files_dict,
                #self.single_signals_metadata,
                ]

    def data_files_dicter(self):

        ch_list = []
        uv_list = []

        for x in self.path.iterdir():
            if x.name.endswith(".ch"):
                ch_list.append(x.name)
            if x.name.endswith(".UV"):

                uv_list.append(x.name)

        return {"ch_files" : ch_list, "uv_files" : uv_list}

    def extract_ch_data(self):
        """
        A function to extraact the ch data from the directory. It was necessary to implement this as a function to provide a 'switch' to parse the data, as that is a slow process.

        Calling this function returns a dict whose keys are the signal wavelengths, and value is a subdict containing the specific signal's information and the data itself.

        I will now be turning the subdict into its own Object so that I can add plotting functionality to it, specifically peak detection and baselines.
        """

        rb_obj = rb.read(str(self.path))

        ch_data_dict = {}

        for file in self.path.iterdir():
            """
            TODO: need to get the dict keys (or output) to be sorted by wavelength from lowest to highest.
            """

            if ".ch" in file.name:

                ch_data = Single_Signal(rb_obj.get_file(str(file.name)), file)
                
                ch_data_dict[ch_data.wavelength] = ch_data
                
        return ch_data_dict

    
    def sequence_name(self):
        
        # note: can only have UPPER CASE naming in Chemstation. Maybe should introduce a lower() function during data read. In fact, should probably include a data cleaning function of some kind. In the mean time, just add upper case to this if statement.
        
        if (".sequence" or ".SEQUENCE") in self.path.parent.name:
            return self.path.parent.name
        else:
            return "single run"
    
    def get_acq_datetime(self):
        with open(self.path / 'RUN.LOG', encoding = '<UTF-16LE>') as f:
            doc = f.read()
            
            idx = doc.index("Method started")
            acq_datetime = datetime.strptime(doc[idx+47:idx+64], "%H:%M:%S %m/%d/%y")
        
            return acq_datetime
                                                
    def load_meta_data(self):
        
        """
        atm this loads the name and description from SAMPLE.XML found in .D dirs.
        It also cleans the description string.
        
        Atm it needs to load the whole XML file to read these two tags, which seems inefficient
        but i dont know how to do it otherwise.
        """
        try:
            with open(self.path / r"SAMPLE.XML", 'r', encoding = 'UTF-16LE') as f:

                xml_data = f.read()
                
                bsoup_xml = BeautifulSoup(xml_data, 'xml')
                
                name = bsoup_xml.find("Name").get_text()
                
                description = bsoup_xml.find("Description").get_text()

                if not description:
                    description = "empty"
                
                else:
                    description = description.replace("\n", "").replace(" ", "-").strip()
                
                acq_method = bsoup_xml.find("ACQMethodPath").get_text().split('\\')[-1]
 
        except Exception as e:
            print(f"error loading metadata from {self.path}: {e}")
    
        return name, description, acq_method 
        
    def rb_object(self):
        """
        loads the whole target data dir, currently it just returns the method and the data.
        """
        rainbow_obj = rb.read(str(self.path))
        
        return rainbow_obj
    
    def load_spectrum(self):

        self.spectrum = UV_Data(self.path)
        self.spectrum.extract_uv_data()
        return self.spectrum

    def __str__(self):
            return str(self.path.parent.parts[-1] + '/' + self.path.name)
# most of the classes were prototypes in 2023-03-02_adding-sequences-to-data-table.ipynb.

# Agilette will be the entry point to all other functionality, analogous to loading the chemstation program.