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
            print(soup_park)
            myMongodb.operations.append(
                pymongo.operations.ReplaceOne(
                    {'name': name},
                    {
                        'name': name,
                        'url-source': url,
                        'address': soup_park.find(class_="sabai-directory-location").text,
                        'phone': soup_park.find(class_="sabai-directory-contact-tel").text,
                        'email': soup_park.find(class_="sabai-directory-contact-email").text,
                        'url-website': soup_park.find(class_="sabai-directory-contact-website").text
                    },
                    upsert=True
                )
            )
            myProxy.sleep()
        except Exception as e:
            print("Error: " + e)
            myProxy.proxy_errors.add(url)
    myMongodb.bulkWrite(collection="sites")
    print("Info: all sites updated. URLs rejected: " + myProxy.proxy_errors)

#Main
if __name__ == "__main__":    

    myMongodb = mdb.Mongodb()
    refreshListing()