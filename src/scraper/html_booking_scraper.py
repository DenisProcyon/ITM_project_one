import aiohttp
from bs4 import BeautifulSoup

class AsyncHTMLBookingScraper:
    PRICE_SELECTOR = 'span.prco-valign-middle-helper'
    NAME_SELECTOR = 'div[data-capla-component-boundary="b-property-web-property-page/PropertyHeaderName"]'
    DESCRIPTION_SELECTOR = 'div[data-capla-component-boundary="b-property-web-property-page/PropertyDescriptionDesktop"]'
    RATING_SELECTOR = 'div[data-testid="review-score-right-component"] > div > div'

    def __init__(self, link: str, session: aiohttp.ClientSession):
        self.link = link
        self.session = session
        self.bs = None

    async def get_bs_engine(self) -> BeautifulSoup:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/102.0.5042.108 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
        }

        async with self.session.get(self.link, headers=headers) as response:
            if response.status == 200:
                html_text = await response.text()
                return BeautifulSoup(html_text, "lxml")
            else:
                raise ConnectionError(f"Request failed with status {response.status}")

    def get_name(self) -> str:
        name_tag = self.bs.select_one(self.NAME_SELECTOR)
        
        return name_tag.text.strip() if name_tag else ""

    def get_hotel_description(self) -> str:
        desc_tag = self.bs.select_one(self.DESCRIPTION_SELECTOR)

        return desc_tag.text.strip() if desc_tag else ""

    def get_rating_data(self) -> tuple[float, float]:
        rating_data = self.bs.select(self.RATING_SELECTOR)
        if not rating_data or len(rating_data) < 2:

            return 0.0, 0.0

        try:
            rating = float(rating_data[0].text.split()[-1])
            reviews = float(rating_data[-1].text.split()[0].replace(",", "."))

            return rating, reviews
        except (ValueError, IndexError):
            return 0.0, 0.0

    def get_price(self) -> float:
        price_tag = self.bs.select_one(self.PRICE_SELECTOR)
        if not price_tag:
            return 0.0

        price_str = price_tag.text
        parsed_price = (price_str.replace("\n€\xa0", "").replace("\n", "").replace(",", "."))
        try:
            return float(parsed_price)
        except ValueError:
            return 0.0

    async def get_data(self) -> dict:
        self.bs = await self.get_bs_engine()
        name = self.get_name()
        hotel_desc = self.get_hotel_description()
        rating, reviews = self.get_rating_data()
        price = self.get_price()

        return {
            "name": name,
            "description": hotel_desc,
            "rating": rating,
            "reviews": reviews,
            "price": price
        }