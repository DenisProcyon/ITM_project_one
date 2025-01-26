from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from enum import Enum

from datetime import datetime
from time import sleep

class Selectors(Enum):
    CITY_INPUT = "input#\\:rh\\:"

    DATE_FIELD = 'button[data-testid="date-display-field-start"]'
    CHECKIN_MONTHS = 'h3[aria-live="polite"]'
    CHECKIN_DATE = "input[data-placeholder='Check-in Date']"
    CHECKOUT_DATE = "input[data-placeholder='Check-out Date']"
    NEXT_PERIOD_BUTTON = 'button[aria-label="Next month"]'

    SEARCH_BUTTON = "button[type='submit']"
    GRID_SEARCH_BUTTON = 'label[for="\\:r72\\:-grid"]'
    CLOSE_WINDOW_BUTTON = 'button[aria-label="Dismiss sign-in info."]'
    SIGN_IN_CLOSE_WINDOW_BUTTON = 'div[aria-label="Fermer"]'
    LOAD_MORE_BUTTON = 'div[style="--bui_box_spaced_padding--s: 4;"] > button'
    HOTEL_LINK = 'a[data-testid="title-link"]'

    COOKIE_ACCEPT_BUTTON = "button#onetrust-accept-btn-handler"

class SelBookingScraper:
    BASE_URL = "https://www.booking.com/"

    def __init__(self, city: str, start_date: str, end_date: str, limit: int = 100) -> None:
        self.city = city
        self.start_date = start_date
        self.end_date = end_date
        self.limit = limit

        Selectors.START_DAY_SELECTOR = f'span[aria-label="{self.start_date}"]'
        Selectors.END_DAY_SELECTOR = f'span[aria-label="{self.end_date}"]'

        if not self.validate_input():
            raise ValueError("Date Validation Error")

        self.setup_driver()

    def validate_input(self):
        try:
            start_ts = datetime.strptime(self.start_date, "%d %B %Y")
            end_ts = datetime.strptime(self.end_date, "%d %B %Y")

            if start_ts > end_ts:
                print("Start date is larger than end date")
                return False
            
            return True
        except ValueError:
            print("Invalid date format. Required e.g.: 1 September 2025")
            return False

    def setup_driver(self):
        self.driver = webdriver.Firefox()
        self.driver.get(self.BASE_URL)

        self.action_chains = ActionChains(self.driver)

    def run_pipeline(self):
        pipeline_order = (
            self.close_cookie_window,
            self.input_city,
            self.input_dates,
            self.search,
            self.load_all_page,
            self.get_hotels_links,
            self.quit_browser
        )
    
        for web_action in pipeline_order:
            sleep(1)
            try:
                web_action()
            except Exception as web_action_exception:
                print(f'Exception occured in {web_action.__name__}: {web_action_exception}. Exiting the loop')

                break

    def __find_elements(self, selector: Selectors):
        return self.driver.find_elements(By.CSS_SELECTOR, selector.value if isinstance(selector, Enum) else selector)

    def __find_element(self, selector: Selectors):
        return self.driver.find_element(By.CSS_SELECTOR, selector.value if isinstance(selector, Enum) else selector)
    
    def get_scraped_hotels_links(self):
        return self.hotels_links
    
    def quit_browser(self):
        self.driver.close()
    
    def close_cookie_window(self):
        sleep(1)
        accept_button = self.__find_element(Selectors.COOKIE_ACCEPT_BUTTON)
        accept_button.click()

    def input_city(self):
        city_input = self.__find_element(Selectors.CITY_INPUT)
        city_input.clear()

        city_input.send_keys(self.city)

    def scroll_to_month(self, month: str, year: str):
        while True:
            try:
                periods = self.__find_elements(Selectors.CHECKIN_MONTHS)
                periods = [period.text for period in periods]
                if f'{month} {year}' in periods:
                    break
                
                print(f'No {month} {year} in {periods}')

                self.__find_element(Selectors.NEXT_PERIOD_BUTTON).click()
            except Exception as e:
                print(f'Can not scroll to {month} {year}')

    def input_dates(self):
        date_field = self.__find_element(Selectors.DATE_FIELD)
        date_field.click()

        start_month, start_year = self.start_date.split()[1:]
        end_month, end_year = self.end_date.split()[1:]

        self.scroll_to_month(start_month, start_year)
        self.__find_element(Selectors.START_DAY_SELECTOR).click()

        self.scroll_to_month(end_month, end_year)
        self.__find_element(Selectors.END_DAY_SELECTOR).click()

    def get_hotels_links(self):
        self.hotels_links = [link.get_attribute("href") for link in self.__find_elements(Selectors.HOTEL_LINK)]

    def load_all_page(self):
        i = 0
        while i < 2: # TODO: we can make it while True but it will take fucking forever in current implementation
            try:
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    sleep(1)

                load_more_button = self.__find_element(Selectors.LOAD_MORE_BUTTON)
                i += 1
            except Exception as e:
                print(f'Page loaded')
                break
            
            load_more_button.click()
            sleep(0.5)

    def search(self):
        self.__find_element(Selectors.SEARCH_BUTTON).click()

        sleep(3)
        try:
            self.__find_element(Selectors.CLOSE_WINDOW_BUTTON).click()
        except Exception as e:
            print(e)

