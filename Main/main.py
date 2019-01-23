import requests
import json
import pprint
import urllib3
from colorama import init, Fore, Back, Style
import time
from bs4 import BeautifulSoup as soup

# grabs all the data from the json file
def getData():
    with open('config.json') as f:
        data = json.load(f)
    return data

#getting data, setting up text formats
data = getData()
pp = pprint.PrettyPrinter(indent=3)
init(convert=True)

# gets all the new products from the shopify site and assigns each item a link
# filtering through the found products to get the product we want, then going to the link and adding to cart
def product_search_atc(session, keywords, monitorDelay):
    productFound = False

    while (productFound == False):
        print("Gathering Products...")
        productDict = {}
        link = 'http://' + data['store'] + '.com/collections/all/products.atom'
        r = session.get(link, verify=False)
        bs = soup(r.text, "html.parser")
        for allProducts in bs.find_all('entry'):
            for products in allProducts.find('title'):
                title = products.lower()
                productLink = products.parent.parent.find('link')['href']
                productDict.update({title: productLink})
        # pp.pprint(productDict)

        print("Successfully gathered products")
        print('-------------------------------------------------------')

        for key in productDict.keys():
            if all(x in key for x in keywords):
                productName = key
                print(Fore.GREEN + "Product Found: " + productName)
                print(Style.RESET_ALL)
                productLink = productDict.get(key)
                # print(productLink)

                r = session.get(productLink, verify=False)

                variantDict = {}

                bs = soup(r.text, "html.parser")
                scripts = bs.findAll('script')
                jsonObj = None

                for s in scripts:
                    if 'var meta' in s.text:
                        script = s.text
                        script = script.split('var meta = ')[1]
                        script = script.split(';\nfor (var attr in meta)')[0]

                        jsonStr = script
                        jsonObj = json.loads(jsonStr)

                for value in jsonObj['product']['variants']:
                    variantSize = value['public_title']
                    variantID = value['id']
                    variantDict.update({variantSize: variantID})

                # print(variantDict)
                return variantDict

        else:
            print(Fore.RED + 'No products found, searching...')
            time.sleep(monitorDelay)

def add_to_cart(session, size):
    variantDict = product_search_atc(session, data['keywords'], data['monitorDelay'])

    for key in variantDict:
        if size in key:
            addToCartVariant = str(variantDict.get(key))
            break
    else:
        print(Fore.RED + "No Such Size")
        return None

    # print(addToCartVariant)

    addedToCart = False
    while addedToCart is False:
        link = "https://" + data['store'] + ".com/cart/add.js?quantity=1&id=" + addToCartVariant
        response = session.get(link, verify=False)
        addToCartData = json.loads(response.text)
        try:
            checkAddToCart = addToCartData["quantity"]
            if (checkAddToCart >= 1):
                print(Fore.CYAN + "Added to Cart")
                return response
        except KeyError:
            print(Fore.RED + "Attempting Add to Cart")
            time.sleep(data["addToCartDelay"])

def start_checkout(session):
    add_to_cart(session, data['size'])
    tempLink = "http://" + data['store'] + '.com//checkout.json'
    response = session.get(tempLink, verify=False, allow_redirects=True)

    print(response.url)

    bs = soup(response.text, "html.parser")
    authToken = bs.find('input', {"name":"authenticity_token"})['value']
    checkout = response.url
    checkoutLink = checkout.replace(data['store'], 'checkout.shopify')
    # Check Stock on Size
    while True:
        if 'stock_problems' in checkoutLink:
            print(Fore.RED + "Size is Not In Stock, Waitng for Restock")
            time.sleep(data["monitorDelay"])
            response = session.get(tempLink, verify=False, allow_redirects=True)
        else:
            print(Fore.GREEN+ "In Stock")
            break

    cookies = session.cookies.get_dict() # gets the cart cookies

    # Check Queue
    print(Fore.WHITE + "Waiting in Queue")
    while True:
        if 'queue' in checkoutLink:
            time.sleep(.1)
        else:
            print(Fore.GREEN + "Passed Queue")
            break

    # Customer Info --------------------------------------------------------------------------------

    # Check if Captcha is present
    captchaPresent = bs.find("div", {"id":"g-recaptcha"})
    if(captchaPresent != None):
        print("Gotta Solve Captcha, Next Update Will be This")
        endingMessage = "Ending Checkout, Click the Checkout Link to Have a Chance at Checkout"
        return endingMessage
    else:
        print(Fore.BLUE + "No Captcha to Solve")

    # Submit Contact Info
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
    }

    payload1 = {
        "utf8": u'\u2713',
        "_method": "patch",
        "authenticity_token": authToken,
        "previous_step": "contact_information",
        "step": "shipping_method",
        "checkout[email]": data['email'],
        "checkout[buyer_accepts_marketing]": "0",
        "checkout[shipping_address][first_name]": data['firstName'],
        "checkout[shipping_address][last_name]": data['lastName'],
        "checkout[shipping_address][address1]": data['streetAddress'],
        "checkout[shipping_address][address2]": "",
        "checkout[shipping_address][city]": data['city'],
        "checkout[shipping_address][country]": data['country'],
        "checkout[shipping_address][province]": data['state'],
        "checkout[shipping_address][zip]": data['zipCode'],
        "checkout[shipping_address][phone]": data['phoneNumber'],
        "checkout[remember_me]": "0",
        "checkout[client_details][browser_width]": "1710",
        "checkout[client_details][browser_height]": "1289",
        "checkout[client_details][javascript_enabled]": "1",
        "button": ""
    }

    while True:
        s = session.post(checkoutLink, cookies=cookies, headers=headers, data=payload1, verify=False)
        if s.status_code is 200:
            print(Fore.YELLOW + "Customer Info Submitted")
            break
        else:
            print(Fore.RED + "Customer Info Error, Retrying...")
            time.sleep(1)

    # Shipping Option
    shipmentOptionLink = "http://" + data['store'] + ".com" + "//cart/shipping_rates.json?shipping_address[zip]=" + data['zipCode'] + "&shipping_address[country]=" + data['country'] + "&shipping_address[province]=" + data['state']
    shipmentOptionLink = shipmentOptionLink.replace(' ', '%20')

    r = session.get(shipmentOptionLink, cookies=cookies, verify=False)
    shipping_options = json.loads(r.text)
    shipping_option = None

    try:
        ship_opt = shipping_options["shipping_rates"][0]["name"].replace(' ', "%20")
        ship_prc = shipping_options["shipping_rates"][0]["price"]
        shipping_option = "shopify-" + ship_opt + "-" + ship_prc
    except KeyError:
        print(Fore.RED + "Error Getting Shipping Token")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
    }

    payload2 = {
        "utf8": u'\u2713',
        "_method": "patch",
        "authenticity_token": authToken,
        "previous_step": "shipping_method",
        "step": "payment_method",
        "checkout[shipping_rate][id]": shipping_option,
        "g-recaptcha-repsonse": "",
        "button": ""
    }

    while True:
        r = session.post(checkoutLink, data=payload2, cookies=cookies, headers=headers)
        if "payment_method" in r.url:
            print(Fore.MAGENTA + "Shipping Method Submitted")
            print(Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Shipping Method Error, Retrying...")
            print(Style.RESET_ALL)



    # Getting gateway token from site
    link = checkoutLink + '?step=payment_method'
    r = session.get(link, cookies=cookies, verify=False)
    bs = soup(r.text, "html.parser")
    div = bs.find("div", {"class": "radio__input"})
    gateway = ""
    values = str(div.input).split('"')
    for value in values:
        if value.isnumeric():
            gateway = value
            break

    # Payment Method --------------------------------------------------------------------------------

    bs = soup(r.text, "html.parser")
    totalPrice = bs.find('input', {'name': 'checkout[total_price]'})['value']
    print(Fore.WHITE + "Total Price: " + totalPrice)

    # Payment
    print(Fore.YELLOW + "Submitting Payment...")
    link = "https://elb.deposit.shopifycs.com/sessions"

    payload3 = {
        "credit_card": {
            "number": data['cardNumber'],
            "name": data['nameOnCard'],
            "month": data['expMonth'],
            "year": data['expYear'],
            "verification_value": data['cvv']
        }
    }

    r = session.post(link, json=payload3, verify=False)
    payment_token = json.loads(r.text)["id"]
    # print(Fore.CYAN + "Payment Token: " + payment_token)


    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'
    }

    payload4 = {
        "utf8": u'\u2713',
        "_method": "patch",
        "authenticity_token": authToken,
        "previous_step": "payment_method",
        "step": "",
        'checkout[buyer_accepts_marketing]': '1', # newsletter
        "s": payment_token,
        "checkout[payment_gateway]": gateway,
        "checkout[different_billing_address]": "false",
        'checkout[credit_card][vault]': 'false',
        'checkout[total_price]': totalPrice,
        "complete": "1",
        "checkout[client_details][browser_width]": '979',
        "checkout[client_details][browser_height]": '631',
        "checkout[client_details][javascript_enabled]": "1",
        "g-recaptcha-repsonse": "",
        "button": ""
    }

    r = session.post(checkoutLink, cookies=cookies, headers=headers, data=payload4, verify=False)

    if r.status_code == 404:
        print(Fore.RED + 'Payment Failed')
    elif r.status_code == 200:
        print(Fore.GREEN + "Maybe a checkout")

session = requests.session()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
start_checkout(session)



