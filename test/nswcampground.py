#python -m pip install pymongo,bs4
import requests, pymongo, mdb, proxy
from bs4 import BeautifulSoup
from datetime import date, timedelta

def refreshListing():
    myProxy = proxy.Proxy()
    response = myProxy.getContent(URL="https://www.caravancampingnsw.com/?view=list")

    if response is not None:
        soup_parks = BeautifulSoup(response, 'html.parser')

        for site in soup_parks.find_all(class_="sabai-directory-title"):
            name=site.text.strip()
            url=site.a['href']

            # r2 = requests.get(url)
            # soup_park = BeautifulSoup(r2.content, 'html.parser')

            myMongodb.operations.append(
                pymongo.operations.ReplaceOne(
                    {'name': name},
                    {
                        'name': name,
                        'urlSource': url
                        # 'address': soup_park.find(class_="sabai-directory-location").text,
                        # 'phone': soup_park.find(class_="sabai-directory-contact-tel").text,
                        # 'email': soup_park.find(class_="sabai-directory-contact-email").text,
                        # 'website': soup_park.find(class_="sabai-directory-contact-website").text
                    },
                    upsert=True
                )
            )

        myMongodb.bulkWrite(collection="sites")
        print("Collection sites refreshed")
    else:
        print("Fatal error")

        
if __name__ == "__main__":    

    myMongodb = mdb.Mongodb()
    refreshListing()