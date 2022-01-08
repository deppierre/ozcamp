from time import sleep
import requests, random

class Proxy:
    
    max_sleep = 5
    nb_proxy = 25
    max_try = 10

    def __init__(self, mdbClient=None):

        self.myMongodb = mdbClient

        self.collection = "proxy"
        self.proxy_list = []
        self.id = 1
        self.proxy_errors = set()

    def getRandomIp(self):
        ip = self.myMongodb.findOneRand(collection = self.collection, filter={"working":True})

        return ip["ipProxy"]

    def insertNewIPsFromFile(self, path):
        with open(path, 'r') as f:
            for newIp in f:
                self.proxy_list.append({
                    "_id": self.id,
                    "ipProxy": "http://" + newIp.strip(),
                    "working": True,
                    "count_fail": 0
                })
                self.id += 1
            print("Info: {0} addresses detected in the file: {1}.".format(self.id, path))

    def sleep(self):
        sleep_time = random.randint(1, Proxy.max_sleep)
        sleep(sleep_time)
        
        print("Info: Next call in {}s".format(sleep_time))

    def getContent(self, URL, proxy=True, ThrowError=False):
        nbTry = 1
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept-Language': 'en-US,en;q=0.5'
        }

        while nbTry <= Proxy.max_try:
            if nbTry == Proxy.max_try: raise Exception("Error: Too many attempts ({0} for URL: {1}).".format(nbTry, URL))
            try:
                session = requests.session()
                if proxy:
                    newIP = self.getRandomIp()
                    if newIP is None: raise Exception("Error: No proxy available.")

                    response = session.get(URL, timeout = 10, proxies = {"http": newIP, "https": newIP}, headers=headers)
                    print("Info: Try {0} with proxy: {1}.".format(nbTry, newIP))
                else:
                    response = session.get(URL, timeout = 10, headers=headers)
                    print("Info: Try {0} without proxy.".format(nbTry))

                return response.content

            except Exception as e:
                print("Warning: Next attempt ({})...".format(nbTry + 1))
                if ThrowError: print(e)
                if newIP is not None: self.myMongodb.updateOne(collection=self.collection, filter={"ipProxy":newIP}, new_value={"$inc": {"count_fail": 1}})
                #self.myMongodb.updateOne(collection=self.collection, filter={"ipProxy":newIP}, new_value={"$set": {"working": False}})
            nbTry += 1

if __name__ == "__main__":
    myProxy = Proxy()
    myProxy.getRandomIp()