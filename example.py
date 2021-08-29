import asyncio

from AsyncParse.proxy import ProxyManager
from AsyncParse.request import RequestManager


loop = asyncio.get_event_loop()  #Start asyncio.EventLoop
target_site = 'http://www.kfc.ru'

proxy_manager = ProxyManager(  
    loop=loop, 
    target=target_site, 
    limit=20, 
    rate=1, 
    timeout=5
) 

proxy_manager.scrape_proxies() #Scrape off all proxies available on free-proxy-list website
proxies = proxy_manager.check_proxies()  #Check with target website if these proxies aren't banned

request_manager = RequestManager(
    loop=loop,
    limit=5,
    rate=1,
    timeout=5
)

request_manager.import_proxies(proxies)  #import proxies to request class

urls = ['https://api.kfc.com/api/store/v2/store.get_restaurants?kfcCityId=13f00203-8aec-4206-bea8-a8c1a159d610']*10

data = request_manager.scrape_urls(urls) #Scrape data from urls using multiple headers and proxies

print(data)

loop.close()  #Close global asyncio.EventLoop