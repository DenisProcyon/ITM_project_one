import asyncio
import aiohttp

from scraper.web_booking_scraper import SelBookingScraper
from scraper.html_booking_scraper import AsyncHTMLBookingScraper

async def main_async():
    data = []

    browser_scraper = SelBookingScraper(city="Barcelona", start_date="1 February 2025", end_date="5 February 2025")
    browser_scraper.run_pipeline()

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

async def fetch_hotel_data(session, index, link, link_num):
    try:
        scraper = AsyncHTMLBookingScraper(link, session)
        hotel_data = await scraper.get_data()
        print(f"{index+1} / {link_num} done", end='\r', flush=True)

        return hotel_data
    except Exception as exc:
        return exc

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()



