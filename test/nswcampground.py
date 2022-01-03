#python -m pip install pymongo,bs4
import requests, pymongo, os
from bs4 import BeautifulSoup
from datetime import date, timedelta
from dotenv import load_dotenv

def getNamespace(collection):

    CONNECTION_STRING = "mongodb+srv://{login}:{password}@testpierre.z01xy.mongodb.net/ozcamp?retryWrites=true&w=majority".format(login=os.environ.get('login'),password=os.environ.get('password'))
    myclient = pymongo.MongoClient(CONNECTION_STRING)

    collection_name = myclient["ozcamp"][collection]

    return collection_name

def insertNewListing(newlisting):

    collection=getNamespace("sites")
    operations=[]

    for newsite in newlisting:
        operations.append(
            pymongo.operations.ReplaceOne(
                {'name': newsite['name']},
                newsite,
                upsert=True
            )
        )

    collection.bulk_write(operations)

def refreshListing():
    newlisting=[]
    r = requests.get('https://www.caravancampingnsw.com/find-holiday-park/')
    soup_holidaypark = BeautifulSoup(r.content, 'html.parser')

    for site in soup_holidaypark.find_all(class_="sabai-directory-title"):
        newlisting.append({
            'name': site.text.strip(),
            'urlSource': site.a['href']
        })

    return newlisting
    
        
if __name__ == "__main__":    

    load_dotenv()

    today = date.today()
    to = today + timedelta(days=4)

    dfrom = today.strftime("%-d+%B+%Y")
    dto = to.strftime("%-d+%B+%Y")
    print(dfrom + ' ' + dto)

    newlisting=refreshListing()

    insertNewListing(newlisting)