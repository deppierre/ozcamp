#!/usr/bin/env python3.9

import asyncio
import calendar
import re
import time
import os
import pymongo
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup

load_dotenv()

today = date.today()
mdb_uri = os.getenv("MONGODB_URI")

#Database
mdb_client = pymongo.MongoClient(mdb_uri)

# Test connection
try:
    mdb_client.server_info()
    print("Connection to MongoDB successful!")
except pymongo.errors.ConnectionFailure:
    print("Connection failed! Please check the MongoDB connection details.")
    exit(1)


# Extract current month and year
max_days = 5
current_month = today.month
current_year = today.year
current_day = today.day
current_date = datetime.today()
one_month_later = today.replace(day=1) + timedelta(days=32)
one_month_later_iso = one_month_later.isoformat()

nb_days = calendar.monthrange(current_year, current_month)[1]
month = calendar.month_name[current_month][0:3]

async def mdb_replace(filter, new_doc, client, db="pierre", coll="nswcampings"):
    try:
        collection = client[db][coll]
        return collection.replace_one(filter, new_doc, upsert=True)
    except Exception as err:
            print(f"An exception occurred ({new_doc}\n{err}")

async def get_html_body(session, URL):
    try:
        session = await session.get(URL)
        await session.html.arender(sleep=1, timeout=20, scrolldown=5)
    except Exception as err:
            print(f"An exception occurred ({URL})\n{err}")

    return session.html

async def process_site(session, site):

    new_camping = {
        "url": "https://" + site,
        "name": "",
        "dates_available": []
    }

    for day in range(current_day, current_day + max_days):
        URL = f"https://{site.strip()}?dateFrom={day}%20{month}%202024&dateTo={day + 1}%20{month}%202024&adults=2"
        print(f"Processing new URL: {URL}")

        htmlbody = await get_html_body(session, URL)
        soup = BeautifulSoup(htmlbody.html, 'html.parser')

        flatpickr_days = soup.find_all(class_="flatpickr-day") #Testing
        availability = soup.find(class_=re.compile(r"d-flex f5 poppins-bold-font mb-2 ml-auto"))
        camping_name = soup.find(class_="show-inline vertical-align-middle")
        
        name = camping_name.text.strip()
        new_camping["name"] = name

        #Changer availability to filter find_all et pas uniquement un seul available. Il doit y avoir dautre trucs a louer que des tentes
        if availability.text == "Available":
            camping_rez_url = soup.find(class_="float-right bg-teal bttn bttn-primary no-underline text-white")
            camping_type = soup.find(class_="availability-description f5 poppins-font mb-3 svelte-9wcegm")

            desired_date = current_date + timedelta(days=day - current_date.day)
            later_date = datetime(desired_date.year, desired_date.month, desired_date.day, 0, 0, 0, 0)

            new_camping["dates_available"].append({
                "ts": later_date,
                "url": camping_rez_url['href'].replace(' ', ''),
                "type": camping_type.find('strong').text
            })

    replace_result = await mdb_replace(
        {"name": name},
        new_camping,
        mdb_client
    )

    if replace_result:
        if replace_result.matched_count > 0:
            print(f"{replace_result.matched_count} documents updated ({name})")
        else:
            print(f"{replace_result.inserted_id} documents inserted ({name})")

async def main():
    session = AsyncHTMLSession()
    added_tasks = []

    with open("test.txt", "r", encoding="utf-8") as sites:
        process_start_time = time.time()

        batch_size = 10
        while True:
            batch_start_time = time.time()
            batch = [next(sites, None) for _ in range(batch_size)]
            batch = [site for site in batch if site is not None]  # Remove None elements

            if not batch:
                break  # End of file

            tasks = [process_site(session, site) for site in batch]
            added_tasks.extend(tasks)

            await asyncio.gather(*tasks)
            await asyncio.sleep(0)  # Let other tasks run

            batch_duration = time.time() - batch_start_time
            print(f"New batch ({batch_size}) processed in {batch_duration:.2f} seconds")
 
    process_duration = time.time() - process_start_time
    print(f"All batches processed in {process_duration:.2f} seconds")
    await session.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())