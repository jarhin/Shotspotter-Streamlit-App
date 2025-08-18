# importing required modules
from pypdf import PdfReader
import re
import os

# for geocoding
from geopy.geocoders import ArcGIS
from pandas import DataFrame
import numpy as np

# for debugging
from pprint import pprint

# helper function
def service_geocode(g_locator, address):
    location = g_locator.geocode(address)
    if location!=None:
      return (location.latitude, location.longitude)
    else:
      return np.NaN

# initialise geocoding
geolocator_arcgis = ArcGIS()

# TODO This script does not work for boxes in the PDF with multiple shooting events.
# Such events were common in the reports from 2018.

class Shot_Events:
    def __init__(self, year: int, page_number: int, path: str):

        # store year
        self.year = year

        # store page number
        self.page_number = page_number

        # store filename
        self.path = path

        # shot info initialised as list
        self.one_file_info_list = []

        # store page info
        self.page_dict = {}

        # dictionary to parse count words into numbers
        self.count_dict = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9
        }

        # string constant for am and pm string checks 
        self.am_pm_checktuple = ("am", "pm", "am.", "pm.", "am,", "pm,")

        # scan lines
        self.current_line = ""
        self.current_line_lower = ""
        self.prev_line = ""
        self.prev_two_line = ""

        # check to see if line has been added in tests
        self.line_previously_added = False

        # initialise shot_event
        self.shot_event = {}

        # proper initialise of shot_event_template
        self.shot_event_template = {
            "location": "", 
            "year": self.year, 
            "shotspotter_alert": "", 
            "string_info": "",
            "additional_details": ""
        }

        # variable based on shot_info
        self.var_shot_info_lower = ""

        # page dict template information
        self.page_dict_template = {'page': self.page_number, "date_string": "", 'path': self.path}

        # dont append text variable - default
        self.var_append_text = True

    def parse_current_line(self, text_line: str) -> None:

        # update previous line variables
        self.prev_two_line = self.prev_line
        self.prev_line = self.current_line_lower

        # store current text line
        self.current_line = text_line

        # default transformation for current text line
        self.current_line_lower = text_line.strip().lower()

        # set line already checked and added as false
        self.line_previously_added = False


    def check_shots_page_date_range(self) -> None:

        # checks
        if self.current_line_lower.startswith(("shootings & shots fired in cambridge:", "confirmed shots fired and shootings in cambridge:")):

            # initialise page info with page
            page_dict = self.page_dict_template.copy()

            # search all date ranges
            date_ranges = re.findall(r"\d{1,2}\.\d{1,2}\.\d{2}|\d{1,2}\/\d{1,2}\/\d{2}", self.current_line_lower)

            # if we can find two dates then construct and store range
            if len(date_ranges) == 2:
                

                # extract digits at top of page and assume date strings
                page_dict["date_string"] = " - ".join(date_ranges)

                # append store page info
                self.page_dict = page_dict


            # change constant as test completed
            self.line_previously_added = True

    def create_var_shot_info_lower(self) -> None:

        self.var_shot_info_lower = self.shot_event["string_info"].lower()


    def find_casings(self) -> None:

        # create variable + use it
        self.create_var_shot_info_lower()

        # find casings
        casings_words = re.search(r"one(?= shell casing)|two(?= shell casings)|three(?= shell casings)|four(?= shell casings)|five(?= shell casings)|six(?= shell casings)|seven(?= shell casings)|eight(?= shell casings)|nine(?= shell casings)", self.var_shot_info_lower)
        casings_words_recovered = re.search(r"one(?= spent round)|two(?= spent rounds)|three(?= spent rounds)|four(?= spent rounds)|five(?= spent rounds)|six(?= spent rounds)|seven(?= spent rounds)|eight(?= spent rounds)|nine(?= spent rounds)", self.var_shot_info_lower)
        casings_number = re.search(r"\d+ (?=shell casing)", self.var_shot_info_lower)
        case_shell_casings = re.search(r"(?<!no) shell casing|bullet recovered|ballistic evidence recovered", self.var_shot_info_lower)
        no_case_shell_casings = re.search(r"no shell casing", self.var_shot_info_lower)
        case_shell_casings_multiple = re.search(r"multiple shell casing|serveral shell casing", self.var_shot_info_lower)

        if casings_words:
            self.shot_event["shell_casings"] =  self.count_dict.get(casings_words.group(), 1)

        if casings_words_recovered:
            self.shot_event["shell_casings"] =  self.count_dict.get(casings_words_recovered.group(), 1)

        if casings_number:
            self.shot_event["shell_casings"] =  casings_number.group()

        if no_case_shell_casings:
            self.shot_event["shell_casings"] = 0 

        if case_shell_casings:
            self.shot_event["shell_casings"] =  1

        if case_shell_casings_multiple:
            self.shot_event["shell_casings"] =  2
    
    def find_multiple_injuries(self) -> None:

        # create variable + use it
        self.create_var_shot_info_lower()
        
        # case multiple injuries (so far max 2)
        case_multiple_injuries = re.findall(r"\d{1,2}-year-old|\d{1,2} year old", self.var_shot_info_lower)
        
        if len(case_multiple_injuries) > 1:
            self.shot_event["injuries"] = len(case_multiple_injuries) 

    def find_no_injuries(self) -> None:

        # create variable + use it
        self.create_var_shot_info_lower()

        # find no injuries
        case_no_injury = re.search(r"no injuries", self.var_shot_info_lower)

        if case_no_injury:
            self.shot_event["injuries"] =  0

    def find_one_injury(self) -> None:

        # find injuries only with start line
        if self.current_line_lower.startswith(("shooting on", "homicide on")):
            self.shot_event["injuries"] =  1

    def find_arrests(self) -> None:

        # create variable + use it
        self.create_var_shot_info_lower()

        # extract arrests
        arrests_words = re.search(r"one(?= arrest)|two(?= arrests)|three(?= arrests)|four(?= arrests)|five(?= arrests)|six(?= arrests)|seven(?= arrests)|eight(?= arrests)|nine(?= arrests)", self.var_shot_info_lower)
        one_arrest = re.search("firearm arrest|suspect arrested|male arrested|female arrested", self.var_shot_info_lower)

        if arrests_words:
            self.shot_event["arrests"] =  self.count_dict.get(arrests_words.group(), 1)

        if one_arrest:
            self.shot_event["arrests"] =  1

    def update_shot_event_with_page_dict(self) -> None:


        if self.page_dict != {}:
        
            # update shot info with page info
            # using unpacking rather than new update operators `|` and `\=` in python 3.9
            self.shot_event = {**self.shot_event, **self.page_dict}

    def update_shot_event_partial_address(self) -> None:

        self.shot_event["partial_address"] = self.shot_event["location"] + ", Cambridge, Massachusetts"
        

    def process_shot_event(self) -> None:

        # append values after whitespace strip
        new_shot_dict = {}
        for key, value in self.shot_event.items():

            if type(value) == str:
                new_shot_dict[key] = value.strip()
            else:
                new_shot_dict[key] = value
        
        # append new_shot_dict to list
        self.one_file_info_list.append(new_shot_dict)

    def initialise_shot_event(self, var_append_text: bool = True) -> None:
        
        # proper initialise
        self.shot_event = self.shot_event_template.copy()

        # set variable to true
        self.var_append_text = var_append_text

    def extract_date_time(self) -> None:
        
        # find WORKING matches to extract dates and times (am and pm)
        # re.match works at the beginning of the string while re.search works throughout the string
        date_match = re.search(r"\d{1,2}\.\d{1,2}", self.current_line)
        time_match = re.search(r"\d{1,2}:\d{2}pm|\d{1,2}:\d{2}am", self.current_line)

        date_match_2 = re.search(r"\d{1,2}\/\d{1,2}", self.current_line)

        # assignments
        if date_match:
            
            # extract date
            temp_date = date_match.group()
            temp_date = temp_date.replace(".", "/")

            # split date into month and day
            temp_month, temp_day = temp_date.split("/")

            # Date in YYYY-MM-DD format
            self.shot_event["date"] = f"{self.year}-{temp_month:0>2}-{temp_day:0>2}"

            # self.shot_event["date"] = temp_date
        if time_match:

            temp_time = time_match.group()

            if 'am' in temp_time:
                temp_time = temp_time.replace("am", "") + " AM"
            if 'pm' in temp_time:
                temp_time = temp_time.replace("pm", "") + " PM"
            
            self.shot_event["time"] = temp_time
        if date_match_2:

            # extract date
            temp_date = date_match_2.group()

            # split date into month and day
            temp_month, temp_day = temp_date.split("/")

            # Date in YYYY-MM-DD format
            self.shot_event["date"] = f"{self.year}-{temp_month:0>2}-{temp_day:0>2}"


            # self.shot_event["date"] = date_match_2.group()

    def process_shot_event_pipeline(self) -> None:

        # store previous shot info removing white spaces in values
        if (self.shot_event != {}) and (self.var_append_text is True):

            # casings, injuries and arrests
            self.find_casings()

            self.find_multiple_injuries()

            self.find_no_injuries()

            self.find_arrests()

            # update shot event with page
            self.update_shot_event_with_page_dict()

            # include partial address
            self.update_shot_event_partial_address()

            # process shot event
            self.process_shot_event()

    def check_shots_shooting_homicide_trigger(self) -> None:

        # test
        if self.current_line_lower.startswith(("shots fired on", "shot fired on", "shooting on", "homicide on")):

            # make sure no previous test run
            if self.line_previously_added is False:

                # process pipeline
                self.process_shot_event_pipeline()

                # initialise shot event
                self.initialise_shot_event()

                # check one injury at start
                self.find_one_injury()

                # extract date time events
                self.extract_date_time()

                # set line added
                self.line_previously_added = True

                # add text to additional_details
                if self.shot_event.get("additional_details", None) is not None:
                    self.shot_event["additional_details"] += self.current_line 

    def there_were_have_been(self) -> None:
        
        if self.current_line_lower.startswith(("there were", "there have been")):

            # make sure no previous test run
            if self.line_previously_added is False:

                # make sure no previous test run
                if self.line_previously_added is False:

                    self.process_shot_event_pipeline()

                    # initialise shot event with var_append_text set to false
                    self.initialise_shot_event(var_append_text = False)

                    # set line added
                    self.line_previously_added = True

    def prev_line_am_pm(self) -> None:

        if self.prev_line.endswith(self.am_pm_checktuple):

            # make sure no previous test run
            if self.line_previously_added is False:

                # add address info to dict
                self.shot_event["location"] += self.current_line
                
                # add text to string info
                if self.shot_event.get("string_info", None) is not None:
                    self.shot_event["string_info"] += self.current_line
                
                # set line added
                self.line_previously_added = True

                # add text to additional_details
                if self.shot_event.get("additional_details", None) is not None:
                    self.shot_event["additional_details"] += " " + self.current_line


    def check_no_shotspotter_alert(self) -> None:
        
        if self.current_line_lower.startswith("no shotspotter alert"):


            # make sure no previous test run
            if self.line_previously_added is False:
                
                # add alert info to dict
                self.shot_event["shotspotter_alert"] = False # "False"

                # add text to string info
                if self.shot_event.get("string_info", None) is not None:
                    self.shot_event["string_info"] += " " + self.current_line

                # set line added
                self.line_previously_added = True

                # add text to additional_details
                if self.shot_event.get("additional_details", None) is not None:
                    self.shot_event["additional_details"] += " " + self.current_line


    def check_shotspotter_alert(self) -> None:

        if self.current_line_lower.startswith("shotspotter alert"):


            # make sure no previous test run
            if self.line_previously_added is False:

                # add alert info to dict
                self.shot_event["shotspotter_alert"] = True # "True"

                # add text to string info
                if self.shot_event.get("string_info", None) is not None:
                    self.shot_event["string_info"] += " " + self.current_line

                # set line added
                self.line_previously_added = True

                # add text to additional_details
                if self.shot_event.get("additional_details", None) is not None:
                    self.shot_event["additional_details"] += " " + self.current_line


    def prev_two_line_am_pm(self) -> None:


        if self.prev_two_line.endswith(self.am_pm_checktuple):


            # make sure no previous test run
            if self.line_previously_added is False:

                # add address info to dict
                self.shot_event["location"] += self.current_line

                # set line added
                self.line_previously_added = True

                # add text to additional_details
                if self.shot_event.get("additional_details", None) is not None:
                    self.shot_event["additional_details"] += self.current_line


    def current_line_am_pm(self) -> None:


        if self.current_line_lower.endswith(self.am_pm_checktuple):

            # make sure no previous test run
            if self.line_previously_added is False:

                self.extract_date_time()

                # add address info to dict
                # shot_event["location"] += text_line

                # set line added
                self.line_previously_added = True
                
                # add text to additional_details
                if self.shot_event.get("additional_details", None) is not None:
                    self.shot_event["additional_details"] += self.current_line

    
    def current_line_shot_include_shot_info(self) -> None:

        # make sure no previous test run
        if self.line_previously_added is False:

            # add text to string info
            if self.shot_event.get("string_info", None) is not None:
                self.shot_event["string_info"] += self.current_line

            # add text to additional_details
            if self.shot_event.get("additional_details", None) is not None:
                self.shot_event["additional_details"] += self.current_line


    def test_lines_order(self) -> None:

        # run tests in order
        self.check_shots_page_date_range()
        self.check_shots_shooting_homicide_trigger()
        self.there_were_have_been()
        self.prev_line_am_pm()
        self.check_no_shotspotter_alert()
        self.check_shotspotter_alert()
        self.prev_two_line_am_pm()
        self.current_line_am_pm()
        self.current_line_shot_include_shot_info()

# directory of PDF
pdf_directory = "./PDF/Monthly Reports/"

# list of files with paths
list_of_files = [os.path.join(pdf_directory, file) for file in os.listdir(pdf_directory)]


# last file by creation date
path_to_last_file = max(list_of_files, key=os.path.getctime)

# path to one file
# pdf_file_path_2024 = "./PDF/Yearly Reports/BridgeStat_December2024_FINAL.pdf"
# pdf_file_path_2023 = "./PDF/Yearly Reports/BridgeStat_December2023_FINAL.pdf"

# file to be parsed
one_file = path_to_last_file

# we assume only one 4 digit number
pdf_year_string = re.findall(r"\d{4}", one_file)[0]

# creating a pdf reader object
one_file = PdfReader(one_file)

# list to store shot info
one_file_info_list = []


for page_count, page in enumerate(one_file.pages, start=1):

    # loop through pages finding shootings and shots fired headers
    if "Shootings" in page.extract_text() and "Shots Fired" in page.extract_text():

        # extract page
        shot_page = page.extract_text().replace(";", "\n")

        # example objects
        example_text_lines = shot_page.split("\n")

        # initialise page object
        current_page_shot_events = Shot_Events(
            year=int(pdf_year_string), 
            page_number = page_count,
            path= path_to_last_file
        )

        # analyse each line
        for text_line in example_text_lines:
            current_page_shot_events.parse_current_line(text_line)
            current_page_shot_events.test_lines_order()

        # parse at end
        # process pipeline
        current_page_shot_events.process_shot_event_pipeline()

        # store events as list of dictionaries
        one_file_info_list.extend(current_page_shot_events.one_file_info_list)



pprint(one_file_info_list)

# update with geolocation in cambridge
for one_dict in one_file_info_list:
    one_dict.update(
        {
            'LAT_LON_arcgis': service_geocode(
                geolocator_arcgis,  
                one_dict["partial_address"]
            )
        }
    )

df = DataFrame(one_file_info_list)


# csv directory
csv_monthly_report_directory = "./CSV/Monthly Reports/"

# We can use a dictionary to extract parts of the filename
month_index_dict = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12"
}


# filename
current_filename_temp = os.path.basename(path_to_last_file).replace(".pdf", ".csv")

# extract month and year
report_month = re.search(r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", current_filename_temp.lower())
report_year = re.search(r"\d{4}", current_filename_temp.lower())

if report_month:
    extact_report_month = month_index_dict.get(report_month.group())

if report_year:
    extact_report_year = report_year.group()

# csv filename prefix
csv_filename_prefix = "BridgeStat_"


current_filename = csv_filename_prefix + extact_report_year + "-" + extact_report_month + "_" + "_".join(current_filename_temp.split("_")[2:])

# write to monthly folder
df.to_csv(os.path.join(csv_monthly_report_directory, current_filename), index=False)

# write file to yearly directory
# check if december is in filename so that it ends up in the yearly report folder
csv_year_directory = "./CSV/Yearly Reports/"

if 'dec' in current_filename.lower():
    
    if current_filename not in os.listdir(csv_year_directory):

        # write to directory
        df.to_csv(os.path.join(csv_year_directory, current_filename), index=False)


