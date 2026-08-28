# Libraries :
from pathlib import Path
import numpy as np
import pandas as pd

####################################
### Configuration  ###
####################################

FIXED_NUM_DEVICES = 100  # Number of devices to be created.

SEED = 42

# Create a random generator object in order to get reproducible data
rng = np.random.default_rng(SEED)

# Input Path 
SCRIPT_DIR = Path(__file__).resolve().parent
DEVICES_PATH = SCRIPT_DIR / "devices_catalog.csv"

# Output Path 
REPO_ROOT = Path(__file__).resolve().parents[2]  # REPO_ROOT => top of git project CWD
OUTPUT_PATH = REPO_ROOT / "data" / "raw" / "devices_raw.csv"


# The catalog_dict will store information about a device type, manufacturear and model
# Later, one device will be picked up  and load it into the devices dict
catalog_dict = {'device_type': [],
                'manufacturer': [],
                'model': [],
                'length': ""
                }


# The devices_dict will store all information required for a wearable device as serial number,
# device type, manufacturer, model and if it support a simcard or not (sim_type).
# Later, it will be converted intoto a tabular format using a dataframe

devices_dict = {'device_serial': [],
                'device_type': [],
                'manufacturer': [],
                'model': [],
                'sim_type': []
}

##############################
# load_devices Function 
##############################
# This function open the device_catalog.csv and load its content into a catalog_dict   

def load_device_catalog():
    
    # Used input path (DEVICES_PATH) to open the file
    with open(DEVICES_PATH, "r", encoding="utf-8") as fhand:
        is_header = True  # Header Flag (the first row of the file has attributes)
        for line in fhand:
            if is_header:  # Check first row and skip attributes/columns
                is_header = False
            else:
                line = line.rstrip()
                split_break = line.split(',') # Separate catalog info in three elements
                catalog_dict['device_type'].append(split_break[0]) # Item 0 goes to device_type
                catalog_dict['manufacturer'].append(split_break[1]) # Item1 goes to manufacturer
                catalog_dict['model'].append(split_break[2]) # Item2 goes to model
        
        #Determine how many rows or items has the catalog.
        # Later the length will be used for picking a device with random generator 
        catalog_dict['length'] = len(catalog_dict['device_type'])
                
        #Debug to test if there are 105 devices in catalog    
        assert catalog_dict['length'] == 105
    
        fhand.close() # Close the device_catalog file 
        return 

##############################
# make_serial_number Function 
##############################
# This function will built a random serial number for devices   
# Received the "i" iterator as input

def make_serial_number(index):
    serial_date = pd.Timestamp("2026-03") # Use a fixed date constant
    hex_tag = f"{rng.integers(0, 0xFFFF):04X}" #Hex number (0000–FFFF) using 4digit
    counter = f"{index:06d}" #Use index to form 6 digit counter (000001-00000i) 
    date_tag = serial_date.strftime("%Y%m") #strftime method will customize the date format
    serial = f"DEV-{date_tag}-{hex_tag}-{counter}"  # Create the serial number
    devices_dict['device_serial'].append(serial) #Store serial number in devices dictionary
    
    return

##############################
# pick_random_device Function 
##############################
# This function will choose a random device from catalog dictionary   

def pick_random_device():
    
    NON_CELLULAR_TYPES = ("fitness_tracker", "glucose_monitor") #These wearables don't use simcard
    SIM_VALUES = ["eSIM", "USIM", "SIM", "iSIM"] # Types of simcard in the market
    SIM_PROBS  = [0.80,   0.12,   0.06,  0.02]  # Probabilities of used simcard. Must sum to 1.0
    
    # Generate a random index
    # The choosen index will be used to pick a device
    random_index = rng.integers(catalog_dict['length']) # Random number from 0 up to but not included length
        
    # Pick the device_type, manufacturer and model ramdonly
    random_device_type = catalog_dict['device_type'][random_index]
    random_manufacturer = catalog_dict['manufacturer'][random_index]
    random_model = catalog_dict['model'][random_index]
    
    # Load the device_type, manufacturer and model into devices dict
    devices_dict['device_type'].append(random_device_type)
    devices_dict['manufacturer'].append(random_manufacturer)
    devices_dict['model'].append(random_model)
        
    
    # Check if the device does NOT support SIMCARD. Write None if not supported.  
    if random_device_type in NON_CELLULAR_TYPES:
        devices_dict['sim_type'].append(None)
    else:
        # Use probabilities of market fo pick up the simcard type
        random_sim_type = rng.choice(SIM_VALUES, p=SIM_PROBS)
        
        # Load the sim_type to the device dictionary   
        devices_dict['sim_type'].append(random_sim_type)
        
    return
    

###############
###  MAIN   ###
###############

load_device_catalog() # Load device_catalog.csv to catalog dictionary

# The devices dictionary will be filled up with iterations
for i in range(1, FIXED_NUM_DEVICES + 1):
    make_serial_number(i) # Function to built a serial number for devices
    pick_random_device() # Function to pick up a device
    
# Generate a dataframe and store in the output_path
dataframe = pd.DataFrame(devices_dict)
dataframe.to_csv(OUTPUT_PATH, index=False) # Dataframe will be saved in a .csv file

