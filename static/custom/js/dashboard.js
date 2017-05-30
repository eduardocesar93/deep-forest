var modalId = -1;
var locked = 0;

var adjustElements = function() {
    $rows = $('.table-editable tbody tr th');
    totalLength = $rows.length;
    for (var i = 0; i < totalLength; i++) {
        $('.table-editable tbody tr th:eq(' + i + ')').html(i);
    }
};

var bSort = function() {
    $rows = $('.table-editable tbody tr th');
    totalLength = $rows.length;
    for (var i = 0; i < totalLength; i++) {
        for (var j = 0; j < (totalLength - i - i); j++) {
            if (parseInt($('.table-editable tbody tr th:eq(' + j + ')').html()) >
                parseInt($('.table-editable tbody tr th:eq(' + (j + 1) + ')').html())
            ) {
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

var addEvents = function() {
    $('.table-remove').click(function() {
        modalId = $(this).parents('tr').index();
        $name = $('.table-editable tbody tr:eq(' + modalId + ') td:eq(0)');
        locked = $('.table-editable tbody tr:eq(' + modalId + ') th:eq(0)').attr("value");
        $('.modal-name').html($name.html())
        $('#myModal').modal('toggle');
        $("input[name=password]").val("");
        if (locked == "0"){
            $("input[name=password]").attr("disabled", true);
        }
        else{
            $("input[name=password]").attr("disabled", false);
        }
    });

    $('.table-up').click(function() {
        var $row = $(this).parents('tr');
        if ($row.index() === 0) return;
        $row.prev().before($row.get(0));
        $('.span-save').show();
        $('.cancel-list').show();
        $('.save-list').show();
    });

    $('.table-down').click(function() {
        var $row = $(this).parents('tr');
        if ($row.parent().children().length == $row.index() + 1) return;
        $row.next().after($row.get(0));
        $('.span-save').show();
        $('.cancel-list').show();
        $('.save-list').show();
    });

    $('.table-down').click(function() {
        var $row = $(this).parents('tr');
        if ($row.parent().children().length == $row.index() + 1) return;
        $row.next().after($row.get(0));
        $('.span-save').show();
        $('.cancel-list').show();
        $('.save-list').show();
    });

    $('td[contenteditable="true"]').bind("DOMSubtreeModified", function(){
        $('.span-save').show();
        $('.cancel-list').show();
        $('.save-list').show();
    });

    $('.save-list').click(function() {
        adjustElements();
        $('.span-save').hide();
        $('.cancel-list').hide();
        $('.save-list').hide();
        var $rows = $("table").find('tr:not(:hidden)');
        var headers = [];
        var data = [];

        $($rows[0]).find('th').each(function () {
            headers.push($(this).text().toLowerCase());
        });

        headers = headers.slice(0, 3);
        $rows = $rows.slice(1, $rows.length);
        $rows.each(function () {
            var $td = $(this).find('td, th');
            var h = {};

            headers.forEach(function (header, i) {
              h[header] = $td.eq(i).text();
            });

            data.push(h);
        });

        $.ajax({
            url: "/atualizar-classificadores?values=" + JSON.stringify(data)
        });
    });


    $('.cancel-list').click(function() {
        bSort();
        $('.span-save').hide();
        $('.cancel-list').hide();
        $('.save-list').hide();
    });
};

var QueryString = function() {
    var query_string = {};
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        if (typeof query_string[pair[0]] === "undefined") {
            query_string[pair[0]] = decodeURIComponent(pair[1]);
        } else if (typeof query_string[pair[0]] === "string") {
            var arr = [query_string[pair[0]], decodeURIComponent(pair[1])];
            query_string[pair[0]] = arr;
        } else {
            query_string[pair[0]].push(decodeURIComponent(pair[1]));
        }
    }
    return query_string;
}();

addEvents();
$('.confirm-delete').click(function() {
    $row = $('.table-editable tbody tr:eq(' + modalId + ')');
    id = $row.find("td:eq(0)").html();
    password = $("input[name=password]").val();
    $.ajax({
        url: "/deletar-classificador?id=" + id + "&password=" + password,
    }).success(function(data){
        if (data == "true"){
            $row.detach();
        }
        else {
            $(".alert-delete").show();
        }
        $('#myModal').modal('toggle');
    });
});

if (QueryString.success && QueryString.success == "true") {
    $(".alert-success").show();
}

if (QueryString.fail && QueryString.fail == "true") {
    $(".alert-fail").show();
}
