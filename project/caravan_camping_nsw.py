#python -m pip install pymongo,bs4
import lib.mdb as mdb
import lib.proxy as proxy

import pymongo
from bs4 import BeautifulSoup

def refreshListing(bulk=False):
    print("Info: Main list collection ...")
    r1 = myProxy.getContent(URL="https://www.caravancampingnsw.com/?view=list")

    print("Info: Main list collected.")
    soup_parks = BeautifulSoup(r1, 'html.parser')
    for site in soup_parks.find_all(class_="sabai-directory-title"):
        name = site.text.strip()
        url = site.a['href']
        try:
            if not myMongodb.findOne(filter={"name":name}):
                r2 = myProxy.getContent(URL=url)
                soup_park = BeautifulSoup(r2, 'html.parser') 
                directory = {
                    "name": name,
                    "urlSource": url,
                }

                if soup_park.find(class_="sabai-directory-location") is not None:
                    directory["address"] = soup_park.find(class_="sabai-directory-location").text.strip()
                if soup_park.find(class_="sabai-directory-contact-tel") is not None:
                    directory["phone"] = soup_park.find(class_="sabai-directory-contact-tel").text.strip()
                if soup_park.find(class_="sabai-directory-contact-tel") is not None:
                    directory["email"] = soup_park.find(class_="sabai-directory-contact-email").text.strip()
                if soup_park.find(class_="sabai-directory-contact-website") is not None:
                    directory["urlWebsite"] = soup_park.find(class_="sabai-directory-contact-website").text.strip()
            
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
            myProxy.proxy_errors.add(name)
    if bulk is True: myMongodb.bulkWrite()
    if len(myProxy.proxy_errors) == 0: total_proxy_errors = 0
    print("Info: Success, process done. URLs rejected: " + str(total_proxy_errors) + "\n - ".join(myProxy.proxy_errors))

#Main
if __name__ == "__main__":    

    myMongodb = mdb.Mongodb(database="ozcamp", collection="sites")
    myMongodb.openNewConnection()

    myProxy = proxy.Proxy(myMongodb)

    refreshListing()