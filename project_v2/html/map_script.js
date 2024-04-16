var locations = {locations};
var map;
var openInfoWindow;
var availableDates = [];

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 7,
        center: { lat: -31.840233, lng: 145.612793 },
        minZoom: 6, // Lock the zoom level
        maxZoom: 12
    });

    // Loop through locations and add markers with info windows
    locations.forEach(function (location) {
        var marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.name
        });

        var infoWindow = new google.maps.InfoWindow({
            content: '<h3>' + location.name + '</h3><p>' + location.details + '</p>'
        });

        marker.addListener('click', function () {
            if (openInfoWindow) {
                openInfoWindow.close();
            }
            infoWindow.open(map, marker);
            openInfoWindow = infoWindow;
        });
    });

    // Extract available dates
    availableDates = locations.reduce(function (dates, location) {
        return dates.concat(location.dates_available);
    }, []);

    // Populate select options
    var dateSelect = document.getElementById('dateSelect');
    availableDates.forEach(function (date) {
        var option = document.createElement('option');
        option.value = date;
        option.text = date;
        dateSelect.appendChild(option);
    });
}

function updateMap() {
    var selectedDate = document.getElementById('dateSelect').value;

    // Clear existing markers
    for (var i = 0; i < map.markers.length; i++) {
        map.markers[i].setMap(null);
    }

    // Add markers for locations available on selected date
    locations.forEach(function (location) {
        if (location.dates_available.includes(selectedDate)) {
            var marker = new google.maps.Marker({
                position: { lat: location.lat, lng: location.lng },
                map: map,
                title: location.name
            });

            var infoWindow = new google.maps.InfoWindow({
                content: '<h3>' + location.name + '</h3><p>' + location.details + '</p>'
            });

            marker.addListener('click', function () {
                if (openInfoWindow) {
                    openInfoWindow.close();
                }
                infoWindow.open(map, marker);
                openInfoWindow = infoWindow;
            });

            map.markers.push(marker);
        }
    });
}

// Store markers on the map object to access them later for removal
map.markers = [];
