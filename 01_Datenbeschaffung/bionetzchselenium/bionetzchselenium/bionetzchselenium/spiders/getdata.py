# -*- coding: utf-8 -*-
import scrapy  # Importing the Scrapy library for web scraping
from scrapy.selector import Selector  # Import Selector for parsing HTML content
from selenium import webdriver  # Import webdriver for controlling the browser
from selenium.webdriver.chrome.options import Options  # Import Options to specify Chrome settings
from selenium.webdriver.chrome.service import Service  # Import Service to manage ChromeDriver
from selenium.webdriver.common.by import By  # Import the By class for locating elements
from webdriver_manager.chrome import ChromeDriverManager  # Import ChromeDriverManager to manage the ChromeDriver binary
from time import sleep  # Import sleep to pause execution for a specified amount of time

# Define a new Scrapy spider class
class GetdataSpider(scrapy.Spider):
    name = 'getdata'  # Name of the spider
    allowed_domains = ['bionetz.ch']  # List of domains the spider is allowed to scrape
    start_urls = ['http://www.bionetz.ch']  # List of starting URLs for the spider

    # The parse method is called with the response object when the spider starts scraping
    def parse(self, response):
        url = 'https://bionetz.ch/adressen/detailhandel/bio-fachgeschaefte.html'  # The URL to scrape

        # Initialize Chrome options for the WebDriver
        options = Options()
        # Uncomment the next line to run Chrome in headless mode (without opening a UI window)
        # options.add_argument('--headless')

        # Initialize the WebDriver with the specified options and auto-install correct ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        # Open the specified URL in the browser
        self.driver.get(url)
        sleep(3)  # Wait for initial page load

        # Loop through all pages
        while True:
            # Create a Selector with the current page source (HTML content)
            sel = Selector(text=self.driver.page_source)
            # Find all elements with the class "bio-listing-card"
            single_etikette = sel.xpath('//*[contains(@class, "bio-listing-card")]')
            # Loop through each element found
            for etikette in single_etikette:
                # Extract the name of the company from the bio-listing-title div
                unternehmens_name = etikette.xpath('.//*[@class="bio-listing-title"]//span/text()').extract_first()
                # Extract the address from the company-address div
                unternehmens_adresse = etikette.xpath('.//*[@class="company-address"]//*[@itemprop="addressLocality"]/text()').extract_first()
                # Yield (return) a dictionary with the company name and address
                yield {'Name': unternehmens_name, 'Adresse': unternehmens_adresse}

            # Check if there's a "Next" button available
            next_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'a.next[aria-label="Weiter"]')
            if not next_buttons:
                # No more pages, exit the loop
                break
            
            # Get the href attribute from the next button and navigate to it
            next_url = next_buttons[0].get_attribute('href')
            self.driver.get(next_url)
            sleep(3)  # Wait for the next page to load

        # Close the WebDriver session and the browser window after scraping is complete
        self.driver.close()
