import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup


class ProxyManager():  #Class used to scrape new proxies and check if they are banned 

    def __init__(self, loop, target, limit, rate, timeout):
        self.loop = loop
        self.target = target
        self.limit = asyncio.Semaphore(limit)
        self.rate = rate
        self.timeout = timeout

    def scrape_proxies(self):  #Get proxies from free-proxy-list
        data = requests.get("https://free-proxy-list.net/").text
        soup = BeautifulSoup(data, 'html.parser')
        table = soup.find('tbody').find_all('tr')
        self.proxies = [
            el.find('td').text + ":" + el.find('td').findNext().text
            for el in table
        ]
        return self.proxies

    async def async_request(self, session, proxy):  #Check if scraped proxies are banned 
        async with self.limit:
            try:
                await session.get(
                    self.target, 
                    proxy='http://'+proxy, 
                    ssl=False, 
                    timeout=self.timeout
                    )
                await asyncio.sleep(self.rate)
                print(f'Successfully added new proxy {proxy}')
                return proxy
            except:
                await asyncio.sleep(self.rate)
                return

    def check_proxies(self): #Check if scraped proxies are banned (eventloop)
        async def async_main():
            async with aiohttp.ClientSession() as session:
                coros = [
                    self.async_request(session, proxy) for proxy in self.proxies
                    ]
                res = await asyncio.gather(*coros)
            return res
        res = self.loop.run_until_complete(async_main())         
        return list(filter(lambda x: bool(x), res))
            

