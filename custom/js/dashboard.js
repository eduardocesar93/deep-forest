var modalId = -1; 

var adjustElements = function(){
    $rows = $('.table-editable tbody tr th');
    totalLength = $rows.length;
    for (var i = 0; i < totalLength; i++){
        $('.table-editable tbody tr th:eq(' + i + ')').html(i);
    }
};

var bSort = function(){
    $rows = $('.table-editable tbody tr th');
    totalLength = $rows.length;
    for (var i = 0; i < totalLength; i++){
        for (var j = 0; j < (totalLength - i - i); j++){
            if (parseInt($('.table-editable tbody tr th:eq(' + j + ')').html()) >
                parseInt($('.table-editable tbody tr th:eq(' + (j + 1) + ')').html())
            ){
                temp = $('.table-editable tbody tr:eq(' + j + ')').html();
                $('.table-editable tbody tr:eq(' + j + ')').html(
                    $('.table-editable tbody tr:eq(' + (j + 1) + ')').html()
                );
                $('.table-editable tbody tr:eq(' + (j + 1) + ')').html(temp);
            }
        }
    }
    addEvents();
};

var addEvents = function(){
    $('.table-remove').click(function () {
        modalId = $(this).parents('tr').index();
        $name = $('.table-editable tbody tr:eq(' + modalId + ') td:eq(0)');
        $('.modal-name').html($name.html())
        $('#myModal').modal('toggle');
    });

    $('.table-up').click(function () {
        var $row = $(this).parents('tr');
        if ($row.index() === 0) return;
        $row.prev().before($row.get(0));
        $('.span-save').show();
        $('.cancel-list').show();
        $('.save-list').show();
    });

    $('.table-down').click(function () {
        var $row = $(this).parents('tr');
        if ($row.parent().children().length == $row.index() + 1) return;
        $row.next().after($row.get(0));
        $('.span-save').show();
        $('.cancel-list').show();
        $('.save-list').show();
    });

    $('.save-list').click(function(){
        adjustElements();
        $('.span-save').hide();
        $('.cancel-list').hide();
        $('.save-list').hide();
    });
    
    
    $('.cancel-list').click(function(){
        bSort();
        $('.span-save').hide();
        $('.cancel-list').hide();
        $('.save-list').hide();
    });
};

var QueryString = function () {
  // This function is anonymous, is executed immediately and 
  // the return value is assigned to QueryString!
  var query_string = {};
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("=");
        // If first entry with this name
    if (typeof query_string[pair[0]] === "undefined") {
      query_string[pair[0]] = decodeURIComponent(pair[1]);
        // If second entry with this name
    } else if (typeof query_string[pair[0]] === "string") {
      var arr = [ query_string[pair[0]],decodeURIComponent(pair[1]) ];
      query_string[pair[0]] = arr;
        // If third or later entry with this name
    } else {
      query_string[pair[0]].push(decodeURIComponent(pair[1]));
    }
  } 
  return query_string;
}();

addEvents();
$('.confirm-delete').click(function(){
    $row = $('.table-editable tbody tr:eq(' + modalId + ')');
    $row.detach();
    $('#myModal').modal('toggle');
});


if (QueryString.success && QueryString.success == "true"){
    $(".alert").show();
}


