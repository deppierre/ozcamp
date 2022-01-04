from time import sleep
from pymongo import collection
import requests, mdb, random, time
from fp.fp import FreeProxy

class Proxy:

    myMongodb = mdb.Mongodb()
    
    max_sleep = 5
    nb_proxy = 25
    max_try = 5

    def __init__(self):
        self.collection = "proxy"
        self.proxy_list = []
        self.id = 1
        self.proxy_errors = set()

    def getRandomIp(self):
        ip = self.myMongodb.findOneRand(filter={"working":True}, collection = self.collection)

        return ip["ipProxy"]

    def insertNewIP(self):
        for newId in range(1, Proxy.nb_proxy + 1):
            print("Info: Progress ... {0} %".format(round(( 100 * newId ) / Proxy.nb_proxy) ))
            newIp = FreeProxy(rand=True, timeout=1, anonym=True, country_id=['AU','US','IN','HK','SG']).get()
            if newIp is not None and 'http://' in newIp:
                self.proxy_list.append({
                    "_id": newId,
                    "ipProxy": newIp,
                    "working": True
                })

    def insertNewIPsFromFile(self, path):
        with open(path, 'r') as f:
            for newIp in f:
                self.proxy_list.append({
                    "_id": self.id,
                    "ipProxy": "http://" + newIp.strip(),
                    "working": True
                })
                self.id += 1
            print("Info: {0} addresses inserted from the file: {1}".format(self.id, path))

    def sleep(self):
        sleep_time = random.randint(1, Proxy.max_sleep)
        time.sleep(sleep_time)
        
        print("Info: next call in {}s".format(sleep_time))

    def getContent(self, URL):
        nbTry = 1
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept-Language': 'en-US,en;q=0.5'
        }

        while nbTry <= Proxy.max_try:
            try:
                newIP = self.getRandomIp()
                if newIP is None: raise Exception("Error: No proxy available")
                print("Info: Try {0} with proxy: {1}".format(nbTry, newIP))

                session = requests.session()
                response = session.get(URL, timeout = 10, proxies = {"http": newIP, "https": newIP}, headers=headers)
                return response.content
            except Exception as e:
                # print("Error: {0}\n next attempt ...".format(str(e)))
                print("Error: next attempt ...")
                if newIP is not None: self.myMongodb.updateOne(collection=self.collection, filter={"ipProxy":newIP}, new_value={"$set": {"working": False}})
            nbTry += 1
        raise Exception("Error: No proxy available")

if __name__ == "__main__":
    myProxy = Proxy()
    myProxy.getRandomIp()