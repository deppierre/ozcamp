#!/usr/bin/env python3.9

import requests
from bs4 import BeautifulSoup

URL="https://www.nationalparks.nsw.gov.au/conservation-and-heritage/national-parks"
URL_DOMAIN=URL.split("/")[2]

#Load all NPs
try:
    response_parks = requests.get(URL, timeout=10)
except Exception as err:
     print(f"An exception occurred ({URL})\n{err}")

soup_parks = BeautifulSoup(response_parks.content, 'html.parser')

print("Loading ...")

for site in soup_parks.find_all(class_="headingIcon icon tree visit"):
    park_name = site.text.strip()
    url = site.a['href']

#Load all campings
    try:
        response_park = requests.get(url, timeout=10)
    except Exception as err:
            print(f"An exception occurred ({URL})\n{err}")
    
    soup_park = BeautifulSoup(response_park.content, 'html.parser')
    campings = soup_park.find_all(class_="scrollingBox__item camping")
    

    if campings:
        for camping in campings:
            URL_CAMPING=URL_DOMAIN + camping.find("h3").a['href']
            with open("nsw_campings.txt", "a", encoding="utf-8") as text_file:
                text_file.write(URL_CAMPING + "\n")