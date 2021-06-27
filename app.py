from bs4 import BeautifulSoup
import cloudscraper
import time, random, calendar
from discord_webhook import DiscordWebhook, DiscordEmbed
import datetime as dt
import json

#Make scraper session object (bypasses Cloudflare anti-bot if necessary) 
def make_scraper():
    browsers = [
        {'browser': 'chrome', 'platform': 'windows', 'mobile': False},
        {'browser': 'chrome', 'platform': 'ios', 'desktop': False},
        {'browser': 'chrome', 'platform': 'android', 'desktop': False}
        ]

    browser = random.choice(browsers)
    scraper = cloudscraper.CloudScraper(interpreter='nodejs', browser = browser)

    return scraper

#Make proxy dictionary for requests
def get_proxy_dict(proxy):
    #If proxy is user authenticated
    if len(proxy.split(":")) == 4:
        ip = proxy.split(":")[0]
        port = proxy.split(":")[1]
        user = proxy.split(":")[2]
        password = proxy.split(":")[3]
        proxy_dict = {"https": f"https://{user}:{password}@{ip}:{port}"}
    #If proxy is ip authenticated
    elif len(proxy.split(":")) == 2:
        ip = proxy.split(":")[0]
        port = proxy.split(":")[1]
        proxy_dict = {"https": f"https://{ip}:{port}"}
    return proxy_dict

#Custom console print
def console_log(message):
    currentDT = calendar.timegm(time.gmtime())
    currentDT = dt.datetime.fromtimestamp(currentDT).strftime('%m/%d/%Y - %H:%M:%S')

    print(f"[{currentDT}] [{message}]")

#Check stock on given profuct sku
def check_stock(scraper, sku, proxy_dict):
    params = {
        "pids": '['+ sku +']',
        "pidObjArray": '{"'+ sku +'":{"pid":'+ sku +',"storeId":"0812"}}'
    }
    try:
        res = scraper.get("https://www.hottopic.com/on/demandware.store/Sites-hottopic-Site/default/Bopis-GetDeliveryOptions?", params=params, proxies = proxy_dict).json()
        
        in_stock = res['products'][sku]['isAvailable']
        if in_stock == "true":
            console_log("Product in stock")
            return {"in_stock": True, "error": False}
        elif in_stock == "false":
            console_log("Product out of stock")
            return {"in_stock": False, "error": False}
    except:
        return {"in_stock": False, "error": True}

#Send discord webhook when item comes back in stock
def send_discord_webhook(discord_webhook, sku, product_details):
    webhook = DiscordWebhook(url=discord_webhook, username="Nova AIO", avatar_url="https://i.ibb.co/WDkZnmC/circle-cropped.png")

    #Set webhook title and color
    product_url = f"https://www.hottopic.com/product/{sku}.html"
    embed = DiscordEmbed(title = product_details['product_title'], url = product_url, color=65280)

    #Set webhook thumbnail
    embed.set_thumbnail(url=product_details['image_url'])

    #Set webhook fields (order details and status)
    embed.add_embed_field(name="Website", value = "Hottopic", inline=True)
    embed.add_embed_field(name="SKU", value = sku, inline=True)
    embed.add_embed_field(name="Price", value = product_details['price'], inline=True)

    #Set message field
    embed.add_embed_field(name="Message", value = "Product is back in stock", inline=False)

    #Set webhook footer
    currentDT = calendar.timegm(time.gmtime())
    currentDT = dt.datetime.fromtimestamp(currentDT).strftime('%m/%d/%Y - %H:%M:%S')
    embed.set_footer(text="Nova AIO | " + currentDT)

    #Add embeds and send to discord
    webhook.add_embed(embed)
    response = webhook.execute()

#Get product details for display on webhook
def get_product_details(scraper, pid, proxy_dict):
    try:
        res = scraper.get(f"https://www.hottopic.com/product/{pid}.html", proxies=proxy_dict)
        soup = BeautifulSoup(res.content, 'lxml')

        product_title = soup.find("h1", attrs={"class": "productdetail__info-title"}).text
        image_url = soup.find("div", attrs={"class":"productdetail__image-thumbnail-each active"}).find("img")['src']
        price = soup.find("span", attrs={"class":"productdetail__info-pricing-original"}).text.strip()
    except:
        product_title = pid
        image_url = "https://pbs.twimg.com/profile_images/890313667379580928/83hx0rNu_400x400.jpg"
        price = "N/A"

    return {"image_url": image_url, "product_title": product_title, "price": price}


def main():
    #Read in settings from json file
    settings = json.load(open('settings.json'))

    #Get scraper object
    scraper = make_scraper()

    #Get proxies from txt file
    proxies = [line.rstrip('\n') for line in open('proxies.txt')]

    #Get proxy dictionary
    proxy_dict = get_proxy_dict(random.choice(proxies))

    stock = check_stock(scraper, settings['sku'], proxy_dict)
    while stock['in_stock'] == False:
        if stock['error'] == True:
            console_log("Error getting stock, switching proxies and scraper")
            time.sleep(settings['timeout']/1000) #prevents spamming endpoint if monitor is broken
            main() #Restart task (new scraper and new proxy selected)
        else:
            time.sleep(settings['timeout']/1000)
            stock = check_stock(scraper, settings['sku'], proxy_dict)
    
    #Get product details and send webhook
    product_details = get_product_details(scraper, settings['sku'], proxy_dict)
    send_discord_webhook(settings['discord_webhook'], settings['sku'], product_details)

main()