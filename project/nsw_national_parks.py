#python -m pip install pymongo,bs4
import lib.mdb as mdb
import lib.proxy as proxy

import pymongo
from bs4 import BeautifulSoup

def refreshListing(bulk=False):
    print("Info: Main list collection ...")
    r1 = myProxy.getContent(URL="https://www.nationalparks.nsw.gov.au/conservation-and-heritage/national-parks", proxy=False)

    print("Info: Main list collected.")
    soup_parks = BeautifulSoup(r1, 'html.parser')
    for site in soup_parks.find_all(class_="headingIcon icon tree visit"):
        park_name = site.text.strip()
        url = site.a['href']
        try:
            r2 = myProxy.getContent(URL=url, proxy=False)
            soup_park = BeautifulSoup(r2, 'html.parser') 
            if soup_park.find(class_="scrollingBox__item camping") is not None:
                print("Info: Camping detected in {}.".format(park_name))
                for site in soup_park.find_all(class_="scrollingBox__item camping"):
                    name = site.find("h3").a.text.strip()
                    directory = {
                        "name": name,
                        "type": "National Park",
                        "nationalParkName": park_name,
                        "urlSource": url,
                        "urlWebsite": "https://www.nationalparks.nsw.gov.au" + site.find("h3").a['href']
                    }
                    if not myMongodb.findOne(filter={"name": name}):
                        if bulk is False:
                            myMongodb.insertOne(document=directory)
                            print("Info: Success, new location created.")
                        else:
                            myMongodb.operations.append(
                                pymongo.operations.ReplaceOne(
                                    {"name": name},
                                    directory,
                                    upsert=True
                                )
                            )
                        myProxy.sleep()
                    else:
                        print("Info: Location already created (name: {0}).".format(name))
                        continue
        except Exception as e:
            print(str(e))
            myProxy.proxy_errors.add(park_name)
            pass
    if bulk is True: myMongodb.bulkWrite()
    if len(myProxy.proxy_errors) == 0: total_proxy_errors = 0
    print("Info: Success, process done. URLs rejected: " + str(total_proxy_errors) + "\n - ".join(myProxy.proxy_errors))

#Main
if __name__ == "__main__":    

    myMongodb = mdb.Mongodb(database="ozcamp", collection="sites")
    myMongodb.openNewConnection()

    myProxy = proxy.Proxy(myMongodb)

    refreshListing()