function htmlEntities(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

class App {

    start() {
        $('#btn_analyse').on('click', function(e){
            var body = $('#inputBody').val();
            var body_enc = {"body": body}

            $('#results_frame').fadeIn(500);
            $.post("api/process", body_enc, function(data, textStatus) {
                $('#indicators').empty();
                var header_highlights = {};
                $.each(data.headers, function(key, value){
                    var outval = '<div class="list-group-item list-group-item-'+value.indicator+'"><h4>'+value.header+'</h4><hr /><p>'+value.data+'</p></div>';
                    $('#indicators').html( $('#indicators').html() + outval );
                    if(value.header in header_highlights) {
                        if(header_highlights[value.header] != "danger") {
                            header_highlights[value.header] = value.indicator;
                        }
                    } else {
                        header_highlights[value.header] = value.indicator;
                    }
                });
                $('#body_raw').html("");
                $.each(data.output_headers, function(key, value) {
                    var row = htmlEntities(key) + ": " + htmlEntities(value);
                    if(key in header_highlights) {
                        row = '<span class="text-'+header_highlights[key]+'">' + row + '</span>';
                    }
                    $('#body_raw').html($('#body_raw').html() + row + "\n");
                });

                $.each(data.attachments, function(key, value){
                    var outval = '<div class="list-group-item list-group-item-'+value.indicator+'"><h4>'+value.header+'</h4><hr /><p>'+value.data+'</p></div>';
                    $('#indicators').html( $('#indicators').html() + outval );
                });

                $.each(data.body, function(key, value){
                    var outval = '<div class="list-group-item list-group-item-'+value.indicator+'"><h4>'+value.name+'</h4><hr /><p>'+value.data.href+' '+value.output+'</p></div>';
                    $('#indicators').html( $('#indicators').html() + outval );
                });

            }, "json");
        });
    }


}