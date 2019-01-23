# DigiBot-V2
Checkout Shopify Bot

# What This Bot Can Do
Currently, this bot is able to find the recently loaded products on a shopify site, around the past 30 loaded products, be able to add to cart and checkout using post and get request. You are able to add some modifications such as monitor delay and add to cart delays, but customization is very limited as of now.

# Tasks to Get Done
1. Add a captcha solving window so that checkouts with captcha will be able to checkout using the bot. This is what I am working on currently. (The files in the project named captcha are just files that are not working as of now). I don't want to use selenium for the captcha harvester so I need to learn some GUI stuff for python to achieve this.

# Setup
1. Install a version of python 3.6 and above here: https://www.python.org/downloads/ , look up tutorials on how to use python on your computer cause it may be a little confuising at first, adding to path...
2. Download all the files on this project into a folder onto your desktop and name that folder whatever you want, lets say "ShopifyBot"
3. Locate the the file called config.json, this is where all the info to run the bot will be stored. Add your name, keywords, billing, shipping addresses, monitor and add to cart delays etc... follow the format I gave you already in the json file, remember to save once done

# Running the Bot
1. Open up the terminal, and locate to the folder that contains the file names "main.py", use this link if you don't know how to do this https://help.ubuntu.com/community/UsingTheTerminal
2. Once in the folder, simply type in "python main.py" to start the bot
3. You should see the bot to start running
