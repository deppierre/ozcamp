import pymongo, os
from dotenv import load_dotenv

class Mongodb:
    load_dotenv()

    login = os.environ.get('login')
    password = password=os.environ.get('password')

    def __init__(self):
        self.db = "ozcamp"
        self.collection = ""
        self.operations=[]

    def getNamespace(self, collection):
        new_client = Mongodb.newConnection()
        namespace = new_client[self.db][collection]

        return namespace

    def insertDropMany(self, collection, documents):
        newNamespace = self.getNamespace(collection)

        newNamespace.drop()
        newNamespace.insert_many(documents)

    def bulkWrite(self, collection):
        newNamespace = self.getNamespace(collection)

        newNamespace.bulk_write(self.operations)

    def find(self, collection):
        newNamespace = self.getNamespace(collection)

        return [ x for x in newNamespace.find() ]

    def findOne(self, filter, collection):
        newNamespace = self.getNamespace(collection)

        return newNamespace.find_one(filter)

    @classmethod
    def newConnection(self):
        connection_string = "mongodb+srv://{login}:{password}@testpierre.z01xy.mongodb.net/ozcamp?retryWrites=true&w=majority".format(login=self.login, password=self.password)
        
        return pymongo.MongoClient(connection_string)