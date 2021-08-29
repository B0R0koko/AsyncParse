import asyncio
import aiohttp

from AsyncParse.utility import ProxyCycle, Decorators, HeadersManager


class RequestManager():  #Class handling requests to target-website

    def __init__(self, loop, limit: int, rate: int, timeout: int):
        self.loop = loop  #Eventloop
        self.limit = asyncio.Semaphore(limit)  #Allows to limit number of asynchronous requests
        self.rate = rate  #Limited number of async requests per num of seconds
        self.headers_manager = HeadersManager()  #Manages changes in headers 
        self.timeout = timeout
        self.proxies = None
        self.requests_num = 0

    def import_proxies(self, proxies: list):  
        self.proxies = ProxyCycle(proxies)
        self.current_proxy = next(self.proxies)
 
    # @Decorators.exception_handler
    async def request(self, session, url, method='GET'):
        async with self.limit:
            async def recursive_request():  #I didnt know how to create recursive coroutine so
                self.requests_num += 1      # I decided to put another function in courotine to do recursion
                print(f'Request number {self.requests_num}')
                try:
                    resp = await session.request(
                        url=url,
                        headers=self.headers_manager.headers,
                        proxy='http://'+self.current_proxy if self.proxies else None,
                        method=method,
                        ssl=False,
                        timeout=self.timeout 
                    )
                    await asyncio.sleep(self.rate)
                    # print(f'Successfully connected to {url} from proxy {self.current_proxy}')
                    return await resp.text()
                except:  
                    # print(f'Error occured trying to connect to {url} from proxy {self.current_proxy}')
                    self.current_proxy = next(self.proxies)
                    await asyncio.sleep(self.rate)
                    return await recursive_request()
            return await recursive_request()  
    
    # @Decorators.exception_handler
    def scrape_urls(self, urls, method='GET'):  #Start eventloop with request method as coroutines

        async def async_main(urls, method):
            async with aiohttp.ClientSession() as session:
                coros = [self.request(session, url, method) for url in urls]
                res = await asyncio.gather(*coros)
                return res
        
        data = self.loop.run_until_complete(async_main(urls, method))
        print(f'Sent {self.requests_num} to fetch {len(urls)}')
        return data