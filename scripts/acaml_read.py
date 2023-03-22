from bs4 import BeautifulSoup as bs

from pathlib import Path

def get_spectrum_info(soup):
    """
    Gets information about spectrum signal datasets, if they exist, from the acq.macaml XML file.
    """


    spectrum_dict = {}

    for section in soup.Content.find_all("Section"):
        if "Spectrum" in section.find('Name').text:
            for parameter in section.find_all('Parameter'):
                if parameter.Name.text == "Spectrum Store":

                    spectrum_start = ""
                    spectrum_end = ""
                    
                    if parameter.Name.text == "All":

                        for name in parameter.find_all('Name'):

                            if "Spectrum Range WL from" in name:
                                
                                spectrum_start = f"{parameter.Value.text} {parameter.Unit.text}"

                            if "Spectrum Range WL to" in name:
                                
                                spectrum_end = f"{parameter.Value.text} {parameter.Unit.text}"
                    
                        spectrum_dict = {"Spectrum Start" : spectrum_start, "Spectrum end" : spectrum_end} 
                    
                    if parameter.Name.text == "None":
                        spectrum_dict = {}

                    # space here for partial spectrums as well.
    return spectrum_dict

def get_single_signal_info(soup):

    """
    Each row has multiple parameters, each which has its own Name, ID, Unit, and Value.
            
    The first parameter asks whether to 'use' the signal, I guess for the trace?

    The second paramter contains the designation of the signal from A to H (?) as Value = 'Signal X' where X is the letter, 
    the third parameter contains the wavelength of the signal, where Unit is 'nm' and 'Value' is the Scalar value of the unit.

    The fourth parameter contains the signal bandwidth, in the same form as the third parameter.

    The fifth parameter covers the use of a reference signal, containing a boolean "Yes" or "No".
    """

    single_signal_dict = {}

    for section in soup.Content.Section:
        if "Signal" in section.text:
            for row in section.Table.find_all('Row'):
                for parameter in row.find_all('Parameter'):
                    if "Signals_Signal_ID" in parameter.find('ID'):
                        
                        id = parameter.Value.text

                        signal_letter = id.split(" ")[1]
                        
                        signal_ID = f"DAD1{signal_letter}.ch"

                    if "Signals_Signal_Wavelength" in parameter.find('ID'):
                        signal_wavelength = f"{parameter.Value.text} {parameter.Unit.text}"
                    
                    if "Signals_Signal_Bandwidth" in parameter.find("ID"):
                        signal_bandwidth = f"{parameter.Value.text} {parameter.Unit.text}"

                single_signal_dict[signal_ID] = {"wavelength" : signal_wavelength,
                    "bandwidth" : signal_bandwidth}

    return single_signal_dict

def signal_metadata(in_path):

    # make the given path a Path object if it isnt already.

    if not isinstance(in_path, Path):
        try:
            in_path = Path(in_path)
        except Exception as e:
            print(f"Could not convert to Path object, {e}")
            return
        
        in_path = in_path / "acq.macaml"

    else:
        in_path = in_path / "acq.macaml"

    if in_path.is_file():

        with in_path.open() as f:

            file = f.read()

            soup = bs(file, 'xml')
        
            return get_single_signal_info(soup), get_spectrum_info(soup)
    
    if not in_path.is_file():
        #print(f"{in_path} does not exist, cannot load signal metadata from acq.macaml")
        return ("empty", "empty")