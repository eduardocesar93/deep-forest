var initBoxes = function(){
	colorPalet = ["rgba(255,0,0,0.9)", "rgba(0,180,0,0.9)"]
	colorPaletWithAlphaZero = ["rgba(255,0,0,0)", "rgba(0,180,0,0)"]
	$colorBoxes = $('.color-box')

	for(var i = 0; i < $colorBoxes.length; i++){
		$($colorBoxes[i]).css('background', colorPalet[i]);
	}
};

var printDeforestationAreas = function(map){
    var rectangleList = [{ // This should be loaded in a ajax call
        classifier: 0,
        bounds:
        [{
            north: -13.5415477,
            south: -13.5415477,
            east:  -69.781962,
            west:  -69.781962,
        },
        {
            north: -13.5415477,
            south: -13.5415477,
            east:  -69.781962,
            west:  -69.781962,
        }]
    },{
        classifier: 1,
        bounds:
        [{
            north: -13.5415477,
            south: -13.5415477,
            east:  -69.781962,
            west:  -69.781962
        },
        {
            north: -13.5415477,
            south: -13.5415477,
            east:  -69.781962,
            west:  -69.781962
        }]
    }]

   for (var i = 0; i < rectangleList.length; i++){
        heatMapData = []
        classifierIndex = rectangleList[i]['classifier'];
        currentColor = colorPalet[classifierIndex];
        currentColorZero = colorPaletWithAlphaZero[classifierIndex];

        for (var j = 0 ; j < rectangleList[i]['bounds'].length; j++){
            for (var k = 0; k < 100000; k++){
                random_X = (Math.random() - 0.5 ) * 5
                random_Y = (Math.random() - 0.5 ) * 5
                var point = {
                    location: new google.maps.LatLng(
                        rectangleList[i]['bounds'][j]['north'] + random_X,
                        rectangleList[i]['bounds'][j]['east'] + random_Y),
                    weight: Math.random()
                };
                heatMapData.push(point);
            }
        }

        var heatmap = new google.maps.visualization.HeatmapLayer({
            data: heatMapData,
            gradient: [  currentColorZero,
                         currentColor
                      ],
            map: map
        });
    }
}

function initMap() {
    var mapCenter = { lat: -7.5415477, lng: -61.781962 };

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: mapCenter
    });

    initBoxes();

    $('#apply-classifier').click(function(event){
        event.preventDefault();
        $.when($('.modal').modal('toggle')).done(function () {
            printDeforestationAreas(map)
            $('.modal').modal('toggle');
        });
    });
}