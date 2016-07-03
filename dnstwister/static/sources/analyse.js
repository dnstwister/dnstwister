$(document).ready(function() {

    var toolMap = {
        parked: function(hexDomain, callback) {
            $.get('/api/parked/' + hexDomain, function(result) {
                var scorePercent = Math.round(result.score * 100);
                var text = result.score_text + ' (' + scorePercent + ' %';
                if (result.redirects === true) {
                    text += ', redirects to: ' + result.redirects_to;
                }
                text += ')';
                callback(text);
            });
        },
    };

    $('.analysis_tool input').click(function() {
        var $section = $(this).parent();
        var toolId = $section.data('id');
        var hexDomain = $section.data('hexdomain');
        var $destination = $section.find('.result');

        $destination.text('Checking...').fadeIn();

        toolMap[toolId](hexDomain, function(text) {
            $destination.text('Result: ' + text);
        });

    });

});
