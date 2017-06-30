function myMap() {
    var mapCanvas = document.getElementById("map");
    var mapOptions = {
        center: new google.maps.LatLng( -22.8898893, -43.3558075),
        zoom: 11
    }
    var map = new google.maps.Map(mapCanvas);
}
