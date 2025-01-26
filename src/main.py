import asyncio
import aiohttp
import pandas as pd
from pathlib import Path

from scraper.web_booking_scraper import SelBookingScraper
from scraper.html_booking_scraper import AsyncHTMLBookingScraper

CITY = "Barcelona"
START = "1 February 2025"
END = "5 February 2025"

async def main_async():
    data = []

    browser_scraper = SelBookingScraper(city=CITY, start_date=START, end_date=END)
    browser_scraper.run_pipeline()

    hotels_file = Path(__file__).parent.parent / f'data/hotels_{CITY}_{START.replace(" ", "_")}_{END.replace(" ", "_")}.csv'

    hotels_links = browser_scraper.get_scraped_hotels_links()
    link_num = len(hotels_links)

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_hotel_data(session, index, link, link_num)
            for index, link in enumerate(hotels_links)
        ]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    for res in raw_results:
        if isinstance(res, Exception):
            print(f"Could not get data: {res}")
        else:
            data.append(res)

    print(f"\nTotal received data: {len(data)} hotels.")

    data = pd.DataFrame(data)
    data.to_csv(hotels_file, index=False)

async def fetch_hotel_data(session, index, link, link_num):
    try:
        scraper = AsyncHTMLBookingScraper(link, session)
        hotel_data = await scraper.get_data()

        print(f"{index + 1} / {link_num} done")

        await asyncio.sleep(0.5)
        return hotel_data

    except Exception as exc:
        return exc

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
