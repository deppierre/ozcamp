#!/usr/bin/env python3.9

import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

mdb_uri = os.getenv("MONGODB_URI")
database = "pierre"

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

nsw_campings = mdb_client[database]["nsw_campings_availability"]
campings_documents = nsw_campings.find({})

# Sample data
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

# HTML template
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Map Display</title>
    <style>
        #map {{
            height: 800px;
            width: 100%;
        }}
    </style>
</head>
<body>
    <div id="map"></div>

    <script>
        var locations = {locations};
        var map;
        var openInfoWindow;

        function initMap() {{
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 7,
                minZoom: 6, // Lock the zoom level
                maxZoom: 12,
                center: {{ lat: -31.840233, lng: 145.612793 }} // Center in NSW
            }});

            // Loop through locations and add markers with info windows
            locations.forEach(function (location) {{
                var marker = new google.maps.Marker({{
                    position: {{ lat: location.lat, lng: location.lng }},
                    map: map,
                    title: location.name
                }});

                var infoWindow = new google.maps.InfoWindow({{
                    content: '<h3>' + location.name + '</h3><p>' + location.details + '</p>'
                }});

                marker.addListener('click', function () {{
                    if (openInfoWindow) {{
                        openInfoWindow.close();
                    }}
                    infoWindow.open(map, marker);
                    openInfoWindow = infoWindow;
                }});
            }});
        }}
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDgTsxuGNQMkjVoiFktxgkP-MgNRqAbpyE&callback=initMap" async defer></script>
</body>
</html>
"""
locations_js = str(locations_array).replace("'", '"')  # Convert to JSON format
html_template = html_template.format(locations=locations_js)

# Write HTML to a file
with open('map_display.html', 'w') as file:
    file.write(html_template)

print("HTML file generated successfully!")
