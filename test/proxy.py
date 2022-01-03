from pymongo import collection
import requests, mdb, random
from fp.fp import FreeProxy

class Proxy:

    myMongodb = mdb.Mongodb()
    
    nb_proxy = 50
    max_try = round( nb_proxy / 2 )

    def __init__(self):
        self.collection = "proxy"
        self.proxy_list = []

    def getRandomIp(self):
        ips = self.myMongodb.find(collection="proxy")
        ip = ips[random.randint(0, len(ips) - 1)]

        return ip['ipProxy']

    def insertNewIP(self):
        for newId in range(1, Proxy.nb_proxy + 1):
            print("Progress ... {0} %".format(round(( 100 * newId ) / Proxy.nb_proxy) ))
            newIp = FreeProxy(rand=True, timeout=1, anonym=True, country_id=['AU','US','IN','HK','SG']).get()
            if newIp is not None and 'http://' in newIp:
                self.proxy_list.append({
                    "_id": newId,
                    "ipProxy": newIp
                })

    def getContent(self, URL):
        nbTry = 1
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept-Language': 'en-US,en;q=0.5'
        }

        while nbTry <= Proxy.max_try:
            try:
                newIP = self.getRandomIp()
                if newIP is not None:
                    print("Try {0} with proxy: {1}".format(nbTry, newIP))
                    response = requests.get(URL, timeout = 10, proxies = {"http": newIP, "https": newIP}, headers=headers)
                    return response.content
                else:
                    print("Error, no Proxy available")
            except Exception as e:
                print("Error: {0}\n next attempt ...".format(str(e)))
            nbTry += 1

if __name__ == "__main__":
    myProxy = Proxy()
    myProxy.getRandomIp()