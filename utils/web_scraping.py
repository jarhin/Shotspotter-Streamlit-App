import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os
import re

# write to csv file
import csv

# base url for searches
base_url = "https://www.cambridgema.gov"

bridgestat_reports_search_url = "https://www.cambridgema.gov/Departments/cambridgepolice/Publications?page=1&ResultsPerPage=10&sortBy=releasedate&sortOrder=desc&keyword=bridgestat"

# bridgestat_reports_search_url = "https://www.cambridgema.gov/search?page=1&keyword=bridgestat+2025&resultsPerPage=10"
bridgestat_reports_search_url_request = requests.get(bridgestat_reports_search_url)

# beautifulsoup request + parse
# decode to utf-8
bridgestat_reports_search_url_soup = BeautifulSoup(
    bridgestat_reports_search_url_request.content.decode("utf-8", errors="ignore"), 
    'html.parser'
)


# find all the rows including url
table_bridgestat_reports_rows = bridgestat_reports_search_url_soup.find_all('tr')

links_to_search = []

# loop through rows to find links
for row in table_bridgestat_reports_rows:
    link = row.find('a')

    # if there is a link make sureit includes detail in the url
    if link:

        if 'detail' in link.get('href'):

            # append to list
            links_to_search.append(
                urljoin(
                    base_url, 
                    link.get('href')
                )
            )

# We take one url by created date
one_report_url = links_to_search[0]

# we scrape the url 
one_report_url_request = requests.get(one_report_url)

# parse the webpage 
# decode to utf-8
one_report_url_soup = BeautifulSoup(
    one_report_url_request.content.decode("utf-8", errors="ignore"), 
    'html.parser'
)


# we extract the "Read More" link from the page 
one_report_url_soup_link = urljoin(
    base_url, 
    one_report_url_soup.find(
        "a", 
        string='Read More'
    ).get('href')
)


# get Wayback Machine Info
requests_session=requests.Session() 
savePage='https://web.archive.org/save/' 
requests_session.get(savePage+one_report_url_soup_link)

first_wayback_machine_url = f"https://web.archive.org/web/0/{one_report_url_soup_link}"

# directory of PDF
pdf_month_directory = "./PDF/Monthly Reports/"

# filename url link info
filename_url_link_file = "./CSV/Filename URL Links/Filename URL Records.csv"

# we extract the filename from the URL
latest_filename = os.path.basename(one_report_url_soup_link)


extact_report_month = ""
extact_report_year = ""

month_dict_report_name = {
    "jan": "Jan",
    "feb": "Feb",
    "mar": "Mar",
    "apr": "Apr",
    "may": "May",
    "jun": "Jun",
    "jul": "Jul",
    "aug": "Aug",
    "sep": "Sep",
    "oct": "Oct",
    "nov": "Nov",
    "dec": "Dec"
}

report_month = re.search(r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec", latest_filename.lower())
report_year = re.search(r"\d{4}", latest_filename.lower())

if report_month:
    extact_report_month = month_dict_report_name.get(report_month.group())

if report_year:
    extact_report_year = report_year.group()


if latest_filename not in os.listdir(pdf_month_directory):

    # get file from url
    pdf_response = requests.get(one_report_url_soup_link)

    # month file path pdf
    monthy_path_pdf = os.path.join(pdf_month_directory, latest_filename)

    # download and write to directory
    with open(monthy_path_pdf, "wb") as pdf_file:

        pdf_file.write(pdf_response.content)

    # write to csv to file
    with open(filename_url_link_file, mode="a") as csv_file:


        csv_headers = ["path", "Report", "Webpage", "PDF URL", "Wayback Machine"]

        # setup object
        writer_object = csv.DictWriter(
            csv_file, 
            fieldnames=csv_headers,
            quoting=csv.QUOTE_STRINGS
        )

        # check if file size is zero and add headers
        if os.stat(filename_url_link_file).st_size == 0:
            writer_object.writeheader()
            
        # write line
        writer_object.writerow(
            {
                "path": monthy_path_pdf, 
                "Report": f"{extact_report_month} {extact_report_year}",
                "Webpage": one_report_url, 
                "PDF URL": one_report_url_soup_link,
                "Wayback Machine": first_wayback_machine_url
            }
        )


# check if december is in filename so that it ends up in the yearly report folder
pdf_year_directory = "./PDF/Yearly Reports/"

if 'dec' in latest_filename.lower():
    
    if latest_filename not in os.listdir(pdf_year_directory):

        # download and write to directory
        with open(os.path.join(pdf_year_directory, latest_filename), "wb") as pdf_file:

            pdf_file.write(pdf_response.content)




