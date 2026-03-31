# Libraries :
from pathlib import Path
import numpy as np
import pandas as pd

####################################
### Configuration  ###
####################################

NUM_MEMBERS = 100  # Number of members to be created.

SEED = 42

# Create a random generator object in order to get reproducible data
rng = np.random.default_rng(SEED)


# Input Path 
SCRIPT_DIR = Path(__file__).resolve().parent
FIRST_NAMES_PATH = SCRIPT_DIR / "first_names.txt"
LAST_NAMES_PATH  = SCRIPT_DIR / "last_names.txt"
AGE_GROUP_PATH   = SCRIPT_DIR / "age_group_by_year.txt"
CITIES_PATH      = SCRIPT_DIR / "cities.txt"


# Output Path 
REPO_ROOT = Path(__file__).resolve().parents[1]  # REPO_ROOT => top of git project CWD
OUTPUT_PATH = REPO_ROOT / "data" / "raw" / "members_raw.csv"


first_name_list = [] # This list will be filled up from the firstname.txt file
last_name_list = [] #  This list will be filled up from the lastname.txt file

# sex_at_birth is limited to biological male/female to match the DB CHECK constraint
sex_at_birth = ['male', 'female']

# The members_dict will store all the key-values related to members table.
# Later, it will be converted to a tabular format using a dataframe
members_dict = {'external_member_id': [],
                'first_name': [],
                'last_name': [],
                'date_of_birth': [],
                'sex_at_birth': [],
                'phone': [],
                'email': [],
                'city': [],
                'state': [],
                'zip_code': [],
                'country': [] 
}

# The location_dict will be used to store cities, states and zip_code
location_dict = {'city': [],
                'state': [],
                'zip_code': []
}

# age_group_dict
# The 'born_year" key will be used to store a year from 1931 to 2008. This means 18-95 years old.
# The 'service_probability' key stores the probability that a year can be used
age_group_dict = {'born_year': [],
                'service_probability': []
}


##############################
# load_first_names Function 
##############################
# This function reads the first_name.txt file and load its content into the first_name list   

def load_first_name_list():
    
    # Used input path (FIRT_NAMES) to open the file
    with open(FIRST_NAMES_PATH, "r", encoding="utf-8") as fhand:
        for line in fhand:
            line = line.rstrip()
            first_name_list.append(line)  
    
    #Debug.  Test if there are 100 first-names    
    assert len(first_name_list) == 100
    
    fhand.close() # Close the first-name file 
    return 

#############################
# load_last_names Function 
##############################
# This function reads the last_name.txt file and load its content into the last_name list 

def load_last_name_list():
    
    # Used input path (LAST_NAMES) to open the file
    with open(LAST_NAMES_PATH, "r", encoding="utf-8") as fhand:
        for line in fhand:
            line = line.rstrip()
            last_name_list.append(line)  
    
    #Debug to test if there are 100 last-names    
    assert len(last_name_list) == 100
    
    fhand.close() # Close the last-name file
    return

#########################################
# load_age_group_by_year Function 
#########################################
def load_age_group_by_year():
# This function open the age_group_by_year.txt file and load its contents into the age_group_dict


# Segmented age-group (This is only an assumption that will be reflected in the age-group file)

#Age-group   Born-Year                           Percentaje of users that will use service
#75+         1931-1951 (include 21 years)        3%  --  3  / 21 = 0.142857% per year (techincal barrier)
#65-74       1952-1961 (include 10 years)        14% --  14 / 10 = 1.4% per year
#55-64       1962-1971 (include 10 years)        25% --  25 / 10 = 2.5% per year
#45-54       1972-1981 (include 10 years)        27% --  27 / 10 = 2.7% per year
#35-44       1982-1991 (include 10 years)        18% --  18 / 10 = 1.8% per year
#25-34       1992-2001 (include 10 years)        10% --  10 / 10 = 1.0% per year
#18-24       2002-2008 (include 7 years)         3%  --   3 / 7 = 0.428571% per year

     
    # Used input path (AGE_GROUP) to open the file
    with open(AGE_GROUP_PATH, "r", encoding="utf-8") as fhand:
        for line in fhand:
            line = line.rstrip()
            split_break = line.split('\t')
            age_group_dict['born_year'].append(split_break[0])
            age_group_dict['service_probability'].append(split_break[1]) 
        
    # Convert string values from key 'service_probability' to float values
    float_probabilities = [float(item) for item in age_group_dict['service_probability']]
   
    # Debug to verify the sum of all probabilites if they are near 100 or 99.9999 
    DEBUG = False
    
    if DEBUG:
        total_probabilities = sum(float_probabilities) #Check if sum probabilites are 100 for age-group
        print(f" The total probabilities among group-ages are: {total_probabilities}")
        dic_length = len(age_group_dict["born_year"])
        print(f" There are {dic_length} different ages between 1931 and 2008")
    
    fhand.close() # Close the age-group file
    return

#############################
# load_cities_list Function 
##############################
def load_cities_list():
    
    # Used input path (CITIES) to open the file
    with open(CITIES_PATH, "r", encoding="utf-8") as fhand:
        for line in fhand:
            line = line.rstrip()
            split_break = line.split('\t')
            location_dict['city'].append(split_break[0])
            location_dict['state'].append(split_break[1]) 
            location_dict['zip_code'].append(split_break[2]) 
    
    # To verify how many cities are in location_dict. There should be 100 cities
    DEBUG = False
    if DEBUG:
        # Determine the length of location_dict and print it
        length = len(location_dict['city'])     
        print(f"There are {length} cities in the list")
        
    
    fhand.close() # Close the cities file
    return


#####################################
# Generate_date_of_birth Function 
#####################################
def generate_date_of_birth(rng):
# This function generates a date of birth in the format yyyy-mm-dd.  It uses the object random generador as input
# The function returns a date_of_birth string  
    
    # Convert string 'service_probabity' values to float. The values are in percentaje.
    service_probability_float = [float(item) for item in age_group_dict['service_probability']]
   
    # Convert each service_probability_float from percentaje to probability (In order to sum 1)
    # It is needed because we will have to normalize the list values to use in rng.choice
    probs = [weights / sum(service_probability_float) for weights in service_probability_float]
       
    # Verify the sum of probabilites.   
    DEBUG = False
    
    if DEBUG:
        without_norm = sum(service_probability_float) #Check if sum probabilites are 100 for age-group
        print(f"Without normalization, sum equals to: {without_norm}")
       
        # This is a requirement from Numpy (sum should be exactly = 1) to use probabilities in rng.choice
        with_norm = sum(probs)
        print(f"After normalization, sum equals to: {with_norm}")
       
  
    # Choose a random year-born using probabilites with weights
    random_year_born = rng.choice(age_group_dict['born_year'], p=probs)
    
    
    # Create a random month from January (1) to December (12)
    random_month_born = rng.integers(1,12)
    
            
    # Determine the number of days that a month can have. Leap year is not taking into account
    if random_month_born == (1 or 3 or 5 or 7 or 8 or 10 or 12): # months can have 31 days
        random_day_born = rng.integers(1,31)
    elif random_month_born == (4 or 6 or 9 or 11): # months can have 30 days
        random_day_born = rng.integers(1,30)  
    else:
        random_day_born = rng.integers(1,28)  # month number 2 (Feb) can have 28 days. 
    
        
    # Verify if month has 1 digit and add "0" to the left
    if len(str(random_month_born)) == 1:
        random_month_born = (f"0{random_month_born}") 
  
    # Verify if day has 1 digit and add "0" to the left
    if len(str(random_day_born)) == 1:
        random_day_born = (f"0{random_day_born}")   
    
        
    # Concatenate (year_born + month + day) to make the date_of_birth variable  
    date_of_birth = str(random_year_born) + "-" + str(random_month_born) + "-" + str(random_day_born)
        
    return date_of_birth
    

###############
###  MAIN   ###
###############

load_first_name_list() # Load first name from a txt file to a list
load_last_name_list()  # Load last name from a txt file to a list
load_age_group_by_year() # Load age-group and stored in a dic
load_cities_list() # Load cities, states, zip_code from a txt file and store in a dictionary




# Fill up the members dictionary using for loop
for i in range(1, NUM_MEMBERS + 1):
    
    first_name = str(rng.choice(first_name_list)) # Choose randomly a first-name
    last_name = str(rng.choice(last_name_list))   # Choose randomly a last-name
    
    #Determine the length of one of the lists of "location_dict" (all should be the same)
    length = len(location_dict['city'])
    
    # Generate a random index to choose city, state and zip_code
    random_index = rng.integers(length) # Random number from 0 up to but not included length
    
    
    ## Choose randomly the city, state and zip_code using the same index
    random_city = location_dict['city'][random_index]
    random_state = location_dict['state'][random_index]
    random_zip_code = location_dict['zip_code'][random_index]
    
      
    # Store key-values in members_dict.  These values will be columns and rows in member table
    members_dict['external_member_id'].append(f"M-{100000+i}")
    members_dict['first_name'].append(first_name)
    members_dict['last_name'].append(last_name)
    members_dict['date_of_birth'].append(generate_date_of_birth(rng))
    members_dict['sex_at_birth'].append(str(rng.choice(sex_at_birth)))
    members_dict['phone'].append(f"+1-555-{rng.integers(1000,9999)}")
    members_dict['email'].append(f"{first_name.lower()}.{last_name.lower()}{i}@example.com")
    members_dict['city'].append(random_city)
    members_dict['state'].append(random_state)
    members_dict['zip_code'].append(random_zip_code)
    members_dict['country'].append("United_States")
      
     
dataframe = pd.DataFrame(members_dict) # Generate a dataframe and store in the output_path
dataframe.to_csv(OUTPUT_PATH, index=False) # Dataframe will be saved in a .csv file
