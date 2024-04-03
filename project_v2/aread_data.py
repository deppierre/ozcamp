#!/usr/bin/env python3.9

import asyncio
import calendar
import time
from datetime import date
from requests_html import AsyncHTMLSession

today = date.today()

# Extract current month and year
current_month = today.month
current_year = today.year
current_day = today.day

nb_days = calendar.monthrange(current_year, current_month)[1]
month = calendar.month_name[current_month][0:3]

bookings = []

async def process_site(session, site):
    for day in range(current_day, current_day + 1):
        URL = f"https://{site.strip()}?dateFrom={day:02d}%20{month}%202024&dateTo={day + 1:02d}%20{month}%202024&adults=2"

        try:
            response_availability = await session.get(URL)
            await response_availability.html.arender(sleep=2, timeout=20)

            name = response_availability.html.xpath('/html/body/div[1]/section/div/div[1]/h1/text()', first=True)

            is_available = False
            rez_url = None
            availability = response_availability.html.xpath('/html/body/div[1]/section/div/div[5]/section[2]/div/div/div/div/div/div/div[1]/span/text()', first=True)
            if availability == "Available":
                is_available = True
                rez_url = response_availability.html.xpath('/html/body/div[1]/section/div/div[5]/section[2]/div/div/div/div/div/div/a/@href', first=True)

            booking = {
                "name": name,
                "source": URL,
                "isAvailable": is_available,
                "rezUrl": rez_url
            }
            
            bookings.append(booking)

        except Exception as err:
            print(f"An exception occurred ({URL})\n{err}")

async def main(loop):
    session = AsyncHTMLSession()
    added_tasks = []

    with open("nsw_campings.txt", "r", encoding="utf-8") as sites:
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
            print(f"New batch {batch_size} processed in {batch_duration:.2f} seconds")
 
    print(bookings)
    process_duration = time.time() - process_start_time
    print(f"All batches processed in {process_duration:.2f} seconds")
    await session.close()

loop = asyncio.get_event_loop()
results = loop.run_until_complete(main(loop))