import time, getpass, selenium
from selenium import common
from selenium.webdriver.common.keys import Keys



class harvest:
    def __init__(self, sitekey, domain, serverip, driver):
        self.driver = driver
        self.sitekey = sitekey
        self.serverip = serverip
        self.domain = domain.replace('https://', 'http://')
        self.htmlcode = "<html><meta name='viewport' content='width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'><head><script type='text/javascript' src='https://www.google.com/recaptcha/api.js'></script><script src='http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js' type='text/javascript'></script> <title>Captcha Harvester</title> <style type='text/css'> body{margin: 1em 5em 0 5em; font-family: sans-serif;}fieldset{display: inline; padding: 1em;}</style></head><body> <center> <h3>Captcha Token Harvester</h3> <h5>HTML by: @pxtvr</h5> <h5>Python by: @Cosm00_</h5> <form action='http://serveriphere:5000/solve' method='post'> <fieldset> <div class='g-recaptcha' data-sitekey='sitekeygoeshere' data-callback='sub'></div><p> <input type='submit' value='Submit' id='submit' style='color: #ffffff;background-color: #3c3c3c;border-color: #3c3c3c;display: inline-block;margin-bottom: 0;font-weight: normal;text-align: center;vertical-align: middle;-ms-touch-action: manipulation;touch-action: manipulation;cursor: pointer;background-image: none;border: 1px solid transparent;white-space: nowrap;padding: 8px 12px;font-size: 15px;line-height: 1.4;border-radius: 0;-webkit-user-select: none;-moz-user-select: none;-ms-user-select: none;user-select: none;'> </p></fieldset> </form> <fieldset> <h5 style='width: 10vh;'> <a style='text-decoration: none;' href='http://serveriphere:5000/json' target='_blank'>Usable Tokens</a> </h5> </fieldset> </center> <script>function sub(){document.getElementById('submit').click();}</script> </body></html>".replace('sitekeygoeshere',
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          self.sitekey).replace('serveriphere', self.serverip)
    def solve(self):
        self.driver.get(self.domain)
        try:
            self.driver.execute_script('document.write("{}")'.format(self.htmlcode))
        except selenium.common.exceptions.WebDriverException:
            pass
        while True:
            if 'Captcha Token Harvester' in self.driver.page_source:
                break
            else:
                pass
        time.sleep(.5)
        try:
            self.driver.execute_script(
                "var evt = document.createEvent('Event');evt.initEvent('load', false, false);window.dispatchEvent(evt);")
        except selenium.common.exceptions.WebDriverException:
            pass
        while True:
            if 'Success' in self.driver.page_source:
                break
            else:
                pass