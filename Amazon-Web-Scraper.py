import selenium
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import TimeoutException
import pandas as pd
import bs4

class Amazon:
    """A class for scraping Amazon product links."""

    def __init__(self):
        self.output = {
            "product_name": [],
            "product_link": [],
            "product description": [],
            "product reviews": [],
        }
        self.page = 2
        self.all_product_links = []
        self.amazon_link = "https://www.amazon.com/"
        self.catogory_link = "https://www.amazon.com/s?i=specialty-aps&bbn=16225006011&rh=n%3A%2116225006011%2Cn%3A11062741&ref=nav_em__nav_desktop_sa_intl_tools_and_accessories_0_2_11_7"
        self.webdriver = webdriver.Chrome()
        self.availble = True
        self.webdriver.get(self.amazon_link)
        time.sleep(2)

    def get_links(self):

        self.webdriver.get(self.catogory_link)
        parser = bs4.BeautifulSoup(self.webdriver.page_source, "html.parser")
        time.sleep(50)
        a_container=parser.find("div", class_="s-main-slot s-result-list s-search-results sg-row")
        links = a_container.find_all("a", class_="a-link-normal s-no-outline")
        for link in links:
            if link["href"].startswith("https"):
                self.all_product_links.append(link["href"])
            else:
                self.all_product_links.append(f"https://amazon.com{link['href']}")


    def next_page(self):

        self.catogory_link = f"{self.catogory_link}&page={self.page}"
        self.webdriver.get(self.catogory_link)
        time.sleep(5)
        try:
            result = self.webdriver.find_elements(By.CSS_SELECTOR, ".sg-col-inner")
            self.get_links()
            print(f"scraping page nun{self.page}")
            self.page += 1

        except TimeoutException:
            self.availble = False

    def scrape_product_details(self):
        for link in self.all_product_links:
            if self.page == 4:
                break
            try:
                self.webdriver.get(link)
                self.all_product_links.remove(link)
                self.product_title = self.webdriver.find_element(By.ID, "productTitle").text
                self.reviews = self.webdriver.find_element(By.ID, "acrCustomerReviewText").text
                self.link = link
                try:
                    show_more = self.webdriver.find_element(By.CLASS_NAME, 'a-expander-prompt')
                    show_more.click()
                    time.sleep(2)
                    self.description = self.webdriver.find_element(By.ID, "feature-bullets").text
                except Exception as e:
                    self.description = "no description"
    
                self.output["product_name"].append(self.product_title)
                self.output["product_link"].append(self.link)
                self.output["product description"].append(self.description)
                self.output["product reviews"].append(self.reviews)
            except Exception as e:
                print(f"Error while scraping link {link}: {str(e)}")

    def scarape_products(self):
        while self.availble:
            if len(self.all_product_links) == 0:
                if self.availble == True:
                    self.next_page()
                    self.scrape_product_details()
            else:
                self.scrape_product_details()

        df = pd.DataFrame(self.output)
        df.to_csv("amazon_products.csv", index=False, encoding='utf-8')
        df.to_excel("amazon_products.xlsx", index=False)
        print("Data has been exported to amazon_products.csv and amazon_products.xlsx")

k = Amazon()
k.get_links()
k.scarape_products()
