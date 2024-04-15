#!/usr/bin/env python3.9

import asyncio
import calendar
import re
import time
import os
import pymongo
import json
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup

load_dotenv()

today = date.today()
mdb_uri = os.getenv("MONGODB_URI")
database = "pierre"

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
max_days = 2
current_month = today.month
current_year = today.year
current_day = today.day

nb_days = calendar.monthrange(current_year, current_month)[1]
month = calendar.month_name[current_month][0:3]

async def mdb_replace(query, new_doc, client, db="pierre", coll="nsw_campings_availability"):
    try:
        collection = client[db][coll]
        return collection.replace_one(query, new_doc, upsert=True)
    except Exception as err:
            print(f"An exception occurred ({new_doc}\n{err}")

async def get_html_body(session, url):
    try:
        session = await session.get(url)
        await session.html.arender(sleep=2, timeout=20, scrolldown=5)
    except Exception as err:
            print(f"An exception occurred ({url})\n{err}")
    return session.html

async def process_site(session, url):
    url_root = url.strip()
    current_date = datetime.today()
    

    print(f"# Processing new site: {url_root}")
    new_camping = {
        "url": url_root,
        "last_update": current_date,
        "dates_available": []
    }

    for day in range(current_day, current_day + max_days):
        url_search_availability = url_root + f"?dateFrom={day}%20{month}%202024&dateTo={day + 1}%20{month}%202024&adults=2"
        print(f"## Processing new day: {url_search_availability}")

        htmlbody = await get_html_body(session, url_search_availability)
        soup = BeautifulSoup(htmlbody.html, 'html.parser')

        flatpickr_days = soup.find_all(class_="flatpickr-day") #Testing
        script_tag = soup.find("script", {"type": "application/ld+json"})
        nb_availability = soup.find_all(class_=re.compile(r"d-flex f5 poppins-bold-font mb-2 ml-auto text-green"))
        camping_name = soup.find(class_="show-inline vertical-align-middle")
        
        name = camping_name.text.strip()
        new_camping["name"] = name

        #JSON data
        if script_tag:
            json_content = json.loads(script_tag.string)
            new_camping["coordinates"] = {
                "latitude": json_content["geo"]["latitude"],
                "longitude": json_content["geo"]["longitude"]
            }
            if "@type" in json_content["address"]:
                del json_content["address"]["@type"]
            new_camping["address"] = json_content["address"]
        else:
            print("No script tag with type 'application/ld+json' found.")

        if len(nb_availability) > 0 and nb_availability[0].text.strip() == "Available":
            camping_rez_url = soup.find(class_="float-right bg-teal bttn bttn-primary no-underline text-white")['href'].replace(' ', ''),
            camping_type = soup.find_all(class_="availability-description f5 poppins-font mb-3 svelte-9wcegm")

            desired_date = current_date + timedelta(days=day - current_date.day)
            later_date = datetime(desired_date.year, desired_date.month, desired_date.day, 0, 0, 0, 0)

            try:
                new_camping["dates_available"].append({
                    "ts": later_date,
                    "url": url_search_availability,
                    "nb_sites": int(len(nb_availability))
                })
            except AttributeError:
                print(f"Error processing this camping URL: {url_search_availability}")

    replace_result = await mdb_replace(
        {"url": url_root},
        new_camping,
        mdb_client
    )

    if replace_result:
        if replace_result.matched_count > 0:
            print(f"{replace_result.matched_count} locations updated ({name})")
        else:
            print(f"New location created ({name})\n\t- {replace_result.upserted_id}")

async def main():
    session = AsyncHTMLSession()
    added_tasks = []

    # Retrieve camping sites from MongoDB collection
    batch_size = 10
    camping_collection = mdb_client[database]["nsw_campings"]
    camping_sites = list(camping_collection.aggregate(
        [
            {"$sort":{"last_update":1}},
            {"$project": {"_id":0, "url":1}}
        ]
    ))
    process_start_time = time.time()

    for i in range(0, len(camping_sites), batch_size):
        batch_start_time = time.time()
        batch = camping_sites[i:i+batch_size]

        tasks = [process_site(session, site["url"]) for site in batch]
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