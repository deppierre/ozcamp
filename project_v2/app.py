#!/usr/bin/env python3.9

import os
from flask import Flask, render_template
import pymongo

app = Flask(__name__)

# Connect to MongoDB

from dotenv import load_dotenv

load_dotenv()
mdb_uri = os.getenv("MONGODB_URI")
myapi_key = os.getenv("GOOGLE_MAP_API_KEY")

#Database
mdb_client = pymongo.MongoClient(mdb_uri)

# Test connection
try:
    mdb_client.server_info()
    print("Connection to MongoDB successful!")
except pymongo.errors.ConnectionFailure as e:
    print("Connection failed! Please check the MongoDB connection details.")
    print(e)
    exit(1)

nsw_campings = mdb_client["pierre"]["nsw_campings_availability"]

@app.route('/html')
def index():
    # Query the collection to find the documents
    campings_documents = nsw_campings.find({})
    
    # Construct the locations array
    locations_array = []

    for camping_document in campings_documents:
        try:
            name = camping_document.get("name", "Unknown").replace("'", '')
            latitude = float(camping_document["coordinates"]["latitude"])
            longitude = float(camping_document["coordinates"]["longitude"])
            details = f"Address: {camping_document['address']['streetAddress']}, {camping_document['address']['addressLocality']}, {camping_document['address']['addressRegion']}, {camping_document['address']['postalCode']}, {camping_document['address']['addressCountry']}"
            locations_array.append({"name": name, "lat": latitude, "lng": longitude, "details": details})
        except KeyError:
            print(f"Skip this camping ... {name}")

    return render_template('index.html', locations=locations_array, api_key=myapi_key)

if __name__ == '__main__':
    app.run(debug=True)