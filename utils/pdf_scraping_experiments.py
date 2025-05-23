# importing required modules
from pypdf import PdfReader
import re

# for debugging
from pprint import pprint


# TODO Find out missing event in given csv
# Shots Fired on 7/4 at
# Approx. 10:00pm; 100
# block of Washington St
# No ShotSpotter alert.
# Shell casings recovered.
# No injuries reported.

# path to one file
pdf_file_path_2024 = "./PDF/Yearly Reports/BridgeStat_December2024_FINAL.pdf"
pdf_file_path_2023 = "./PDF/Yearly Reports/BridgeStat_December2023_FINAL.pdf"

# file to be parsed
one_file = pdf_file_path_2024

# we assume only one 4 digit number
pdf_year_string = re.findall(r"\d{4}", one_file)[0]

# creating a pdf reader object
one_file = PdfReader(one_file)

count_dict = {
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


# dont append text
var_append_text = True


# page info list
page_info_list = []

# list to store shot info
one_file_info_list = [] 

# extract text page headers
# loop through all pages of file finding certain text.
# we start at one to store information later
for page_count, page in enumerate(one_file.pages, start=1):

    # loop through pages finding shootings and shots fired headers
    if "Shootings" in page.extract_text() and "Shots Fired" in page.extract_text():

        # initialise page info with page
        page_dict = {
            'page': page_count,
            "date_string": ""
        }

        # extract page
        shot_page = page.extract_text().replace(";", "\n")

        # example objects
        example_text_lines = shot_page.split("\n")
        example_page_lines = []

        # add end trigger so that all dictionaries created for shots are parsed.
        example_text_lines_plus_trigger = example_text_lines + ["shots fired on"]

        # scan lines
        prev_line = ""
        prev_two_line = ""

        # shot_event initialise
        shot_event = {}

        # analyse each line
        for text_line in example_text_lines_plus_trigger:

            # startswith can accept tupples to check multiple values
            if text_line.strip().lower().startswith(("shootings & shots fired in cambridge:", "confirmed shots fired and shootings in cambridge:")):
                example_page_lines.append(1)

                # extract digits at top of page and assume date strings
                page_dict["date_string"] = " - ".join(re.findall(r"\d{,2}\.\d{,2}\.\d{,2}", text_line))

                # append page info to list
                page_info_list.append(page_dict)


                

            elif text_line.strip().lower().startswith(("shots fired on", "shot fired on", "shooting on", "homicide on")):
                example_page_lines.append(2)

                
                # store previous shot info removing white spaces in values
                if (shot_event != {}) and (var_append_text is True):
                    
                    # TODO create and parse string info properly

                    # find casings
                    casings_words = re.search(r"one(?= shell casing)|two(?= shell casings)|three(?= shell casings)|four(?= shell casings)|five(?= shell casings)|six(?= shell casings)|seven(?= shell casings)|eight(?= shell casings)|nine(?= shell casings)", shot_event["string_info"].lower())
                    casings_words_recovered = re.search(r"one(?= spent round)|two(?= spent rounds)|three(?= spent rounds)|four(?= spent rounds)|five(?= spent rounds)|six(?= spent rounds)|seven(?= spent rounds)|eight(?= spent rounds)|nine(?= spent rounds)", shot_event["string_info"].lower())
                    casings_number = re.search(r"\d+ (?=shell casing)", shot_event["string_info"].lower())
                    case_shell_casings = re.search(r"(?<!no) shell casing|bullet recovered|ballistic evidence recovered", shot_event["string_info"].lower())
                    no_case_shell_casings = re.search(r"no shell casing", shot_event["string_info"].lower())
                    case_shell_casings_multiple = re.search(r"multiple shell casing|serveral shell casing", shot_event["string_info"].lower())

                    if casings_words:
                        shot_event["shell_casings"] =  count_dict.get(casings_words.group(), 1)

                    if casings_words_recovered:
                        shot_event["shell_casings"] =  count_dict.get(casings_words_recovered.group(), 1)

                    if casings_number:
                        shot_event["shell_casings"] =  casings_number.group()

                    if no_case_shell_casings:
                        shot_event["shell_casings"] = 0 

                    if case_shell_casings:
                        shot_event["shell_casings"] =  1

                    if case_shell_casings_multiple:
                        shot_event["shell_casings"] =  2

                    # case multiple injuries (so far max 2)
                    case_multiple_injuries = re.findall(r"\d{2}-year-old|\d{2} year old", shot_event["string_info"].lower())
                    
                    if len(case_multiple_injuries) > 1:
                        shot_event["injuries"] = len(case_multiple_injuries) 
                    
                    # find no injuries
                    case_no_injury = re.search(r"no injuries", shot_event["string_info"].lower())

                    if case_no_injury:
                        shot_event["injuries"] =  0

                    # extract arrests
                    arrests_words = re.search(r"one(?= arrest)|two(?= arrests)|three(?= arrests)|four(?= arrests)|five(?= arrests)|six(?= arrests)|seven(?= arrests)|eight(?= arrests)|nine(?= arrests)", shot_event["string_info"].lower())
                    one_arrest = re.search("firearm arrest|suspect arrested|male arrested|female arrested", shot_event["string_info"].lower())

                    if arrests_words:
                        shot_event["arrests"] =  count_dict.get(arrests_words.group(), 1)

                    if one_arrest:
                        shot_event["arrests"] =  1

                    # append values after whitespace strip
                    new_shot_dict = {}
                    for key, value in shot_event.items():

                        if type(value) == str:
                            new_shot_dict[key] = value.strip()
                        else:
                            new_shot_dict[key] = value
                    
                    # append new_shot_dict to list
                    one_file_info_list.append(new_shot_dict)

                # proper initialise
                shot_event = {"location": "", "year": pdf_year_string, "shotspotter_alert": "", "string_info": ""}

                # find injuries only with start line
                if text_line.strip().lower().startswith(("shooting on", "homicide on")):
                    shot_event["injuries"] =  1

                # set variable to true
                var_append_text = True

                # TODO find WORKING matches to extract dates and times (am and pm)
                # re.match works at the beginning of the string while re.search works throughout the string
                date_match = re.search(r"\d{1,2}\.\d{1,2}", text_line)
                time_match = re.search(r"\d{1,2}:\d{2}pm|\d{1,2}:\d{2}am", text_line)

                date_match_2 = re.search(r"\d{1,2}\/\d{1,2}", text_line)

                # assignments
                if date_match:
                    shot_event["date"] = date_match.group()
                    shot_event["date"] = shot_event["date"].replace(".", "/")
                if time_match:
                    shot_event["time"] = time_match.group()
                if date_match_2:
                    shot_event["date"] = date_match_2.group()

            elif text_line.strip().lower().startswith(("there were", "there have been")):
                example_page_lines.append(-1)

                # set variable to true
                var_append_text = False

                # TODO Trigger parsing of shot dict here

            elif prev_line.strip().lower().endswith(("am", "pm", "am.", "pm.", "am,", "pm,")):
                example_page_lines.append(3)

                # add address info to dict
                shot_event["location"] += text_line
                
                # add text to string info
                if shot_event.get("string_info", None) is not None:
                    shot_event["string_info"] += text_line

            elif text_line.strip().lower().startswith(("no shotspotter alert")):
                
                example_page_lines.append(4)

                # add alert info to dict
                shot_event["shotspotter_alert"] = False # "False"

                # add text to string info
                if shot_event.get("string_info", None) is not None:
                    shot_event["string_info"] += " " + text_line
            
            elif text_line.strip().lower().startswith(("shotspotter alert")):
                example_page_lines.append(4)

                # add alert info to dict
                shot_event["shotspotter_alert"] = True # "True"

                # add text to string info
                if shot_event.get("string_info", None) is not None:
                    shot_event["string_info"] += " " + text_line

            # we assume at most two lines for the address including those lines broke by the semicolon
            elif prev_two_line.strip().lower().endswith(("am", "pm", "am.", "pm.", "am,", "pm,")):
                example_page_lines.append(3)

                # add address info to dict
                shot_event["location"] += text_line
            # previous line is shooting statement
            elif text_line.strip().lower().endswith(("am", "pm", "am.", "pm.", "am,", "pm,")):
                example_page_lines.append(2)

                # date extraction
                date_match = re.search(r"\d{1,2}\.\d{1,2}", text_line)
                time_match = re.search(r"\d{1,2}:\d{2}pm|\d{1,2}:\d{2}am", text_line)

                date_match_2 = re.search(r"\d{1,2}\/\d{1,2}", text_line)

                # assignments
                if date_match:
                    shot_event["date"] = date_match.group()
                if time_match:
                    shot_event["time"] = time_match.group()
                if date_match_2:
                    shot_event["date"] = date_match_2.group()

                # add address info to dict
                # shot_event["location"] += text_line
            else:
                example_page_lines.append(0)

                # add text to string info
                if shot_event.get("string_info", None) is not None:
                    shot_event["string_info"] += text_line


            # store last line
            prev_two_line = prev_line
            prev_line = text_line


pprint(page_info_list)
pprint(one_file_info_list)



# TODO search pages for Shootings & Shots Fired in Cambridge
# https://stackoverflow.com/questions/12571905/finding-on-which-page-a-search-string-is-located-in-a-pdf-document-using-python
