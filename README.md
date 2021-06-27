## Description
This is a restock monitor for the Hottopic website. The script will continuously check if the product is in stock and notify you via a discord webhook.

Hottopic releases limited edition funko pops and restocks products randomly, it is heavily botted. This script will help the average consumer who does not have access to these bots by notifying them as soon as a product restocks.
## Usage
In the settings JSON file, you will have to specify the product SKU, timeout, and discord webhook. The timeout is in milliseconds, the default delay is 1500, anything lower will most likely trigger Hottopic's anti-bot and restrict access. You can find the product SKU under the product details section of the product page.

You will also need to use proxies by placing them into the proxies.txt file. Each proxy should be separated by a new line. Both user authenticated and IP authenticated proxies are supported.

Run the script by using:
```
python app.py
```



## Discord Notification
When an item goes back in stock you will receive a notification like the following to your discord webhook.

![alt text](https://i.ibb.co/R04g01Y/discord-example.jpg)
