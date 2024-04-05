#!/usr/bin/env python3.9

import calendar
from datetime import date
from requests_html.requests_html import HTMLSession

today = date.today()

# Extract current month and year
current_month = today.month
current_year = today.year
current_day = today.day

session = HTMLSession()

nb_days = calendar.monthrange(current_year, current_month)[1]
month = calendar.month_name[current_month][0:3]

bookings = []

with open("test.txt", "r", encoding="utf-8") as text_file:
    for line in text_file:
        print(f"Processing {line}")

        for day in range(current_day, current_day + 1):
            URL = "https://www.nationalparks.nsw.gov.au/camping-and-accommodation/campgrounds/colo-meroo-campground?dateFrom=17%20Apr%202024&dateTo=18%20Apr%202024&adults=2"

            try:
                response_availability = session.get(URL)
                response_availability.html.render(sleep=2)

                if response_availability.status_code != 200:
                    raise Exception(f"HTML Session error ({response_availability.status_code})") 
            except Exception as err:
                print(f"An exception occurred ({URL})\n{err}")
            else:
                booking = {
                    "name": None,
                    "source": response_availability.url,
                    "isAvailable": False,
                    "rezUrl": None
                }
                
                booking["name"] = response_availability.html.xpath('/html/body/div[1]/section/div/div[1]/h1/text()', first=True)
                
                if response_availability.html.xpath('/html/body/div[1]/section/div/div[5]/section[2]/div/div/div/div/div/div/div[1]/span/text()', first=True) == "Available": 
                    booking["isAvailable"] = True
                    booking["rezUrl"] = response_availability.html.xpath('/html/body/div[1]/section/div/div[5]/section[2]/div/div/div/div/div/div/a/@href', first=True)

                # print(f"source: {response_availability.url} dest: {rezUrl} isAvailable: {isAvailable}")
                bookings.append(booking)

print(bookings)