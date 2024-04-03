import pymongo, os, random
from dotenv import load_dotenv

class Mongodb:
    load_dotenv()

    login = os.environ.get('login')
    password = os.environ.get('password')

    def __init__(self, database, collection):
        self.db = database
        self.collection = collection
        self.operations=[]

    def openNewConnection(self, db=None):
        if db is None: db = self.db

        self.client = Mongodb.newConnection(db)

    def insertDropMany(self, documents, collection=None):
        if collection is None: collection = self.collection
        collection = self.client[self.db][collection]

        collection.drop()
        collection.insert_many(documents)

    def insertOne(self, document, collection=None):
        if collection is None: collection = self.collection
        collection = self.client[self.db][collection]

        collection.insert_one(document)

    def bulkWrite(self, collection=None):
        if collection is None: collection = self.collection
        collection = self.client[self.db][collection]

        collection.bulk_write(self.operations)

    def findOneRand(self, filter, collection=None):
        if collection is None: collection = self.collection
        collection = self.client[self.db][collection]

        coll_size = collection.count()

        while True:
            rand_skip = random.randint(0, coll_size)
            for doc in collection.find(filter).skip(rand_skip).sort("count_fail", 1).limit(1):
                if doc is not None: return doc

    def findOne(self, filter, collection=None):
        if collection is None: collection = self.collection
        collection = self.client[self.db][collection]

        return collection.find_one(filter)

    def updateOne(self, filter, new_value, collection=None):
        if collection is None: collection = self.collection
        collection = self.client[self.db][collection]

        collection.update_one(filter, new_value)

    @classmethod
    def newConnection(self, db):
        connection_string = "mongodb+srv://{login}:{password}@cluster0.pc1yqzp.mongodb.net/{db}?retryWrites=true&w=majority&appName=Cluster0".format(login=self.login, password=self.password, db=db)
        
        return pymongo.MongoClient(connection_string)