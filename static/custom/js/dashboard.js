$( document ).ready(function(){
    var modalId = -1;
    var locked = 0;

    var adjustElements = function() {
        $rows = $('.table-editable.classifiers tbody tr th:nth-child(2)');
        totalLength = $rows.length;
        for (var i = 0; i < totalLength; i++) {
            $('.table-editable.classifiers tbody tr th:nth-child(2):eq(' + i + ')').html(i);
        }
    };

    var bSort = function() {
        $rows = $('.table-editable.classifiers tbody tr th');
        totalLength = $rows.length;
        for (var i = 0; i < totalLength; i++) {
            for (var j = 0; j < (totalLength - i - 1); j++) {
                if (parseInt($('.table-editable.classifiers tbody tr th:nth-child(2):eq(' + j + ')').html()) >
                    parseInt($('.table-editable.classifiers tbody tr th:nth-child(2):eq(' + (j + 1) + ')').html())
                ) {
                    temp = $('.table-editable.classifiers tbody tr:eq(' + j + ')').html();
                    $('.table-editable.classifiers tbody tr:eq(' + j + ')').html(
                        $('.table-editable.classifiers tbody tr:eq(' + (j + 1) + ')').html()
                    );
                    $('.table-editable.classifiers tbody tr:eq(' + (j + 1) + ')').html(temp);
                }
            }
        }
        addEvents();
    };

    var addEvents = function() {
        $('.classifiers .table-remove').click(function() {
            modalId = $(this).parents('tr').index();
            $name = $('.table-editable.classifiers tbody tr:eq(' + modalId + ') td:eq(1)');
            locked = $('.table-editable.classifiers tbody tr:eq(' + modalId + ') th:eq(0)').attr("value");
            $('.modal-name').html($name.html())
            $('.modal.classifiers').modal('toggle');
            $("input[name=password]").val("");
            if (locked == "0"){
                $("input[name=password]").attr("disabled", true);
            }
            else{
                $("input[name=password]").attr("disabled", false);
            }
        });

        $('.classifiers .table-info').click(function() {
            modalId = $(this).parents('tr').index();
            $row = $('.table-editable.classifiers tbody tr:eq(' + modalId + ')');
            $name = $('.table-editable.classifiers tbody tr:eq(' + modalId + ') td:eq(1)');
            $('.modal-name').html($name.html());
            id = $row.find("td:eq(0)").html();
            $.ajax({
                url: "/obter-classificador?id=" + id,
                dataType: 'json'
            }).success(function(data){
                $('.modal.classifiers-info .modal-body').html(
                    "<span> <b>Nome</b>: " + data.name + "</span><br>" +
                    "<span> <b>Tipo do Classificador</b>: " + data.type_classifier + "</span><br>" +
                    "<span> <b>Método de Otimização</b>: " + data.optimization_method + "</span><br>" +
                    "<span> <b>Função de Ativação</b>: " + data.activation_function + "</span><br>" +
                    "<span> <b>Acurácia</b>: " + data.accuracy + "</span><br>" +
                    "<span> <b>Status</b>: " + data.state + "</span><br>" +
                    "<span> <b>Tamanho do Batch</b>: " + data.batch + "</span><br>" +
                    "<span> <b>Taxa de Aprendizagem</b>: " + data.learning_rate + "</span><br>" +
                    "<span> <b>Número de Épocas</b>: " + data.number_epochs + "</span><br>"
                );
                $('.modal.classifiers-info').modal('toggle');
            });
        });

        $('.datasets .table-remove').click(function() {
            modalId = $(this).parents('tr').index();
            $name = $('.table-editable.datasets tbody tr:eq(' + modalId + ') td:eq(1)');
            $('.modal-name').html($name.html())
            $('.modal.datasets').modal('toggle');
            $("input[name=password]").val("");
        });

        $('.classifiers .table-up').click(function() {
            var $row = $(this).parents('tr');
            if ($row.index() === 0) return;
            $row.prev().before($row.get(0));
            $('.span-save').show();
            $('.cancel-list').show();
            $('.save-list').show();
        });

        $('.classifiers .table-down').click(function() {
            var $row = $(this).parents('tr');
            if ($row.parent().children().length == $row.index() + 1) return;
            $row.next().after($row.get(0));
            $('.span-save').show();
            $('.cancel-list').show();
            $('.save-list').show();
        });

        $('.classifiers .table-down').click(function() {
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
            var $rows = $(".classifiers table").find('tr:not(:hidden)');
            var headers = [];
            var data_classifiers = [];

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

                data_classifiers.push(h);
            });

            var $rows = $(".datasets table").find('tr:not(:hidden)');
            var headers = [];
            var data_datasets = [];

            $($rows[0]).find('th').each(function () {
                headers.push($(this).text().toLowerCase());
            });

            headers = headers.slice(0, 2);
            $rows = $rows.slice(1, $rows.length);
            $rows.each(function () {
                var $td = $(this).find('td, th');
                var h = {};

                headers.forEach(function (header, i) {
                  h[header] = $td.eq(i).text();
                });

                data_datasets.push(h);
            });

            $.ajax({
                url: "/atualizar-classificadores?classifiers=" + JSON.stringify(data_classifiers)
                + "&datasets=" + JSON.stringify(data_datasets)
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
    $('.classifiers .confirm-delete').click(function() {
        $row = $('.table-editable.classifiers tbody tr:eq(' + modalId + ')');
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
            $('.modal.classifiers').modal('toggle');
        });
    });

    $('.datasets .confirm-delete').click(function() {
        $row = $('.table-editable.datasets tbody tr:eq(' + modalId + ')');
        id = $row.find("td:eq(0)").html();
        $.ajax({
            url: "/deletar-dataset?id=" + id,
        }).success(function(data){
            if (data == "true"){
                $row.detach();
            }
            else {
                $(".alert-delete").show();
            }
            $('.modal.datasets').modal('toggle');
        });
    });

    if (QueryString.success && QueryString.success == "true") {
        $(".alert-success").show();
    }

    if (QueryString.fail && QueryString.fail == "true") {
        $(".alert-fail").show();
    }
});
