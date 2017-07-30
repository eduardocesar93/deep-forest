colorPalet = ["rgba(255,0,0,0.9)", "rgba(0,180,0,0.9)",
                  "rgba(0,0,200,0.9)", "rgba(0,100,100,0.9)", "rgba(80,80,80,0.9)"]
colorPaletWithAlphaZero = ["rgba(255,0,0,0)", "rgba(0,180,0,0)",
                            "rgba(0,0,200,0)", "rgba(0,100,100,0)", "rgba(80,80,80,0)"]

var initBoxes = function(){

	$colorBoxes = $('.color-box')

	for(var i = 0; i < $colorBoxes.length; i++){
		$($colorBoxes[i]).css('background', colorPalet[i]);
	}
};

var interpolation = function(i, j, total_i, total_j, lat_inf, lng_inf, lat_sup, lng_sup){
    int_lat_sup = ((total_i - i) * lat_sup + i * lat_inf) / (total_i)
    int_lat_inf = ((total_i - i - 1)* lat_sup + (i  + 1)* lat_inf) / (total_i)
    int_lng_sup = ((total_j - j) * lng_sup + j * lng_inf) / (total_j)
    int_lng_inf = ((total_j - j - 1)* lng_sup + (j + 1) * lng_inf) / (total_j)

    return {
            'lat' : (int_lat_inf + int_lat_sup) / 2,
            'lng' : (int_lng_inf + int_lng_sup) / 2
        }
};

var angle_to_decimal = function(angle){
    direction = angle[angle.length - 1]
    angle = angle.substring(0, angle.length - 1)
    if (direction == 'S' || direction == 's' ||
        direction == 'W' || direction == 'w'){
        return parseFloat(angle) * (-1)
    }
    else {
        return parseFloat(angle)
    }
};

var convert_matrix = function(matrix_dict){
    lat_inf = angle_to_decimal(matrix_dict['lat_lng']['lat_inf'])
    lat_sup = angle_to_decimal(matrix_dict['lat_lng']['lat_sup'])
    lng_inf = angle_to_decimal(matrix_dict['lat_lng']['lng_inf'])
    lng_sup = angle_to_decimal(matrix_dict['lat_lng']['lng_sup'])
    matrix = matrix_dict['cover']
    list_points = []
    for (var i = 0; i < matrix.length; i++){
        for (var j = 0; j < matrix[i].length; j++){
            position = interpolation(i, j, matrix.length, matrix[i].length,
                                     lat_inf, lng_inf, lat_sup, lng_sup);
            if (matrix[i][j] < 0){
                list_points.push([position, Math.min(1, matrix[i][j] / (-5))])
            }
        }
    }

    return list_points
}

var printDeforestationAreas = function(map, list_points, classifierIndex){
    heatMapData = []
    currentColor = colorPalet[classifierIndex];
    currentColorZero = colorPaletWithAlphaZero[classifierIndex];

    for (var i = 0 ; i < list_points[i].length; i++){
        console.log(list_points[i]);
        var point = {
            location: new google.maps.LatLng(
                list_points[i][0]['lat'],
                list_points[i][0]['lng']),
            weight: list_points[i][1]
        };
        heatMapData.push(point);
    }

    console.log(currentColorZero);
    console.log(currentColor);
    var heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatMapData,
        gradient: [  currentColorZero,
                     currentColor
                    ],
        map: map
    });

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

        dataset_first = $('select[name=dataset_first]').val();
        dataset_last = $('select[name=dataset_last]').val();
        classifier = $('input[name=classifier]:checked').val();

        index = -1
        currentIndex = 0;
        $('input[name=classifier]').each(function(){
            value = $(this).val();
            if (value == classifier){
                index = currentIndex;
                if (classifier && dataset_last && dataset_first){
                    $.ajax({
                        url: "/classificar-images?classifier=" + classifier
                        + "&first=" + dataset_first +
                        "&last=" + dataset_last,
                        dataType: 'json',
                        success: function(data){
                            console.log("aqui");
                            console.log(index);
                            list_points = convert_matrix(data);
                            console.log(list_points);
                            printDeforestationAreas(map, list_points, index);
                        }
                    });
                }
            }
            currentIndex++;
        });

        // $.when($('.modal').modal('toggle')).done(function () {
        //     printDeforestationAreas(map)
        //     $('.modal').modal('toggle');
        // });
    });
}