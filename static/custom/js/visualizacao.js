colorPalet = ["rgba(0,180,0,0.9)", "rgba(255,0,0,0.9)",
                  "rgba(0,0,200,0.9)", "rgba(0,100,100,0.9)", "rgba(80,80,80,0.9)"]
colorPaletWithAlphaZero = ["rgba(0,180,0,0)", "rgba(255,0,0,0)",
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

    return [list_points, {'lat' : (lat_inf + lat_sup)/ 2, 'lng' : (lng_inf + lng_sup)/2 }]
}

var printDeforestationAreas = function(map, list_points, classifierIndex){
    heatMapData = []
    currentColor = colorPalet[classifierIndex];
    currentColorZero = colorPaletWithAlphaZero[classifierIndex];

    max_lat = -10000;
    min_lat = 10000;
    max_lng = -10000;
    min_lng = 10000;

    for (var i = 0 ; i < list_points.length; i++){
        var point = {
            location: new google.maps.LatLng(
                list_points[i][0]['lat'],
                list_points[i][0]['lng']),
            weight: list_points[i][1]
        };
        console.log(list_points[i][0]['lat']);
        if (list_points[i][0]['lat'] < min_lat){
            min_lat = list_points[i][0]['lat'];
        }
        if (list_points[i][0]['lat'] > max_lat){
            max_lat = list_points[i][0]['lat'];
        }
        if (list_points[i][0]['lng'] > max_lng){
            max_lng = list_points[i][0]['lng'];
        }
        if (list_points[i][0]['lng'] < min_lng){
            min_lng = list_points[i][0]['lng'];
        }
        heatMapData.push(point);
    }

    var heatmap = new google.maps.visualization.HeatmapLayer({
        data: heatMapData,
        gradient: [  currentColorZero,
                     currentColor
                    ],
        map: map,
        radius: 50
    });

    return { lat: (min_lat + max_lat)/2, lng: (min_lng + max_lng)/2 };
}

function initMap() {
    var mapCenter = { lat: -4.0042978, lng: -58.7201982 };

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 6,
        center: mapCenter
    });

    map.setOptions({maxZoom: 13});

    initBoxes();

    $('.spinner').removeClass('hidden');
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
                        beforeSend: function(){
                            $('.modal').modal('toggle');
                            console.log("Wait for response...");
                        },
                        success: function(data){
                            converted_matrix = convert_matrix(data);
                            list_points = converted_matrix[0];
                            zoom = 12;
                            latLngMinimal = printDeforestationAreas(map, list_points, index);
                            if (latLngMinimal['lat'] != 0 || latLngMinimal['lng'] != 0){
                                converted_matrix[1] = latLngMinimal;
                                zoom = 13;
                            }
                            map.panTo(converted_matrix[1]);
                            map.setZoom(zoom);
                            console.log("Complete!");
                        },
                        complete: function(){
                            $('.modal').modal('toggle');
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