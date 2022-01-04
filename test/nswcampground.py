#python -m pip install pymongo,bs4
import requests, pymongo, mdb, proxy
from bs4 import BeautifulSoup
from datetime import date, timedelta

def refreshListing():
    myProxy = proxy.Proxy()
    r1 = myProxy.getContent(URL="https://www.caravancampingnsw.com/?view=list")

    print("Info: Main list collected ")
    soup_parks = BeautifulSoup(r1, 'html.parser')
    for site in soup_parks.find_all(class_="sabai-directory-title"):
        name = site.text.strip()
        url = site.a['href']
        try:
            r2 = myProxy.getContent(URL=url)
            soup_park = BeautifulSoup(r2, 'html.parser') 

            directory = {
                "name": name,
                "urlSource": url,
            }

            if not myMongodb.findOne(filter={"name":name}, collection="sites"):
                if soup_park.find(class_="sabai-directory-location") is not None:
                    directory["address"] = soup_park.find(class_="sabai-directory-location").text.strip()
                if soup_park.find(class_="sabai-directory-contact-tel") is not None:
                    directory["phone"] = soup_park.find(class_="sabai-directory-contact-tel").text.strip()
                if soup_park.find(class_="sabai-directory-contact-tel") is not None:
                    directory["email"] = soup_park.find(class_="sabai-directory-contact-email").text.strip()
                if soup_park.find(class_="sabai-directory-contact-website") is not None:
                    directory["urlWebsite"] = soup_park.find(class_="sabai-directory-contact-website").text.strip()

                myMongodb.insertOne(collection="sites",document=directory)
                print("Info: New location created")

                myProxy.sleep()
            else:
                print("Info: Location already created")
            # myMongodb.operations.append(
            #     pymongo.operations.ReplaceOne(
            #         {"name": name},
            #         directory,
            #         upsert=True
            #     )
            # )
        except Exception as e:
            print("Error: " + e)
            myProxy.proxy_errors.add(url)
    myMongodb.bulkWrite(collection="sites")
    print("Info: all sites updated. URLs rejected: " + myProxy.proxy_errors)

#Main
if __name__ == "__main__":    

    myMongodb = mdb.Mongodb()
    refreshListing()