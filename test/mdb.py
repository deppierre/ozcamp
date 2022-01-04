import pymongo, os, random
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

    def insertOne(self, collection, document):
        newNamespace = self.getNamespace(collection)

        newNamespace.insert_one(document)

    def bulkWrite(self, collection):
        newNamespace = self.getNamespace(collection)

        newNamespace.bulk_write(self.operations)

    def findOneRand(self, filter, collection):
        newNamespace = self.getNamespace(collection)
        coll_size = newNamespace.count()

        while True:
            rand_skip = random.randint(0, coll_size)
            for doc in newNamespace.find(filter).skip(rand_skip).limit(1):
                if doc is not None: return doc

    def findOne(self, filter, collection):
        newNamespace = self.getNamespace(collection)

        return newNamespace.find_one(filter)

    def updateOne(self, filter, new_value, collection):
        newNamespace = self.getNamespace(collection)

        newNamespace.update_one(filter, new_value)

    @classmethod
    def newConnection(self):
        connection_string = "mongodb+srv://{login}:{password}@testpierre.z01xy.mongodb.net/ozcamp?retryWrites=true&w=majority".format(login=self.login, password=self.password)
        
        return pymongo.MongoClient(connection_string)