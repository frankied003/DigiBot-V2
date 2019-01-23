import logging
import time

class ChromeLogin():

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    emailfield = "//*[@type='email']"
    passfield = "//*[@name='password']"
    passedLogin = "Control, protect, and secure your account, all in one place"

    def login(self):

        print("You need to sign into chrome for captcha to work")
        self.driver.get('https://accounts.google.com/signin/v2')
        while True:
            if 'Manage your info' in self.driver.page_source:
                break
            elif 'Control, protect' in self.driver.page_source:
                break
            else:
                continue
        time.sleep(1)

    def redirectToStore(self, domain):
        shopifyWebsite = "https://" + domain + ".com/sitemap_products_1.xml"
        self.driver.get(shopifyWebsite)
        return domain
