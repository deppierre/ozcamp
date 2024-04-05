#!/usr/bin/env python3.9

import asyncio
import calendar
import time
from datetime import date, datetime, timedelta
from requests_html.requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup

today = date.today()

# Extract current month and year
current_month = today.month
current_year = today.year
current_day = today.day
current_date = datetime.today()
one_month_later = today.replace(day=1) + timedelta(days=32)
one_month_later_iso = one_month_later.isoformat()

nb_days = calendar.monthrange(current_year, current_month)[1]
month = calendar.month_name[current_month][0:3]

async def get_html_body(session, URL):
    try:
        session = await session.get(URL)
        await session.html.arender(sleep=2, timeout=20, scrolldown=5)
    except Exception as err:
            print(f"An exception occurred ({URL})\n{err}")

    return session.html

async def process_site(session, site):
    new_camping = {
        "url": site,
        "name": "",
        "dates_available": []
    }

    for day in range(current_day, current_day + 4):
        URL = f"https://{site.strip()}?dateFrom={day}%20{month}%202024&dateTo={day}%20{month}%202024&adults=2"
        
        htmlbody = await get_html_body(session, URL)

        #changer pour BS
        name = htmlbody.xpath('/html/body/div[1]/section/div/div[1]/h1/text()', first=True)
        
        availability = htmlbody.xpath('/html/body/div[1]/section/div/div[5]/section[2]/div/div/div/div/div/div/div[1]/span/text()', first=True)
        if availability == "Available":
            #check quel type dans Box-row pb-5
            Box-row pb-5
            rez_url = htmlbody.xpath('/html/body/div[1]/section/div/div[5]/section[2]/div/div/div/div/div/div/a/@href', first=True)

            delta = day - current_day
            later_date = ( current_date + timedelta(days=delta) ).timestamp()

            new_camping["name"] = name
            new_camping["dates_available"].append({
                "ts": int(later_date),
                "url": rez_url,
                "type": ""
            })

        print(URL)

    print(new_camping)


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