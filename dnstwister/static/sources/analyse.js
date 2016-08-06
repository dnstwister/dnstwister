$(document).ready(function() {

    var toolMap = {
        parked: function(hexDomain, success, error) {
            $.get('/api/parked/' + hexDomain, function(result) {
                var scorePercent = Math.round(result.score * 100);
                var text = result.score_text + ' (' + scorePercent + ' %';
                if (result.redirects === true) {
                    text += ', redirects to: ' + result.redirects_to;
                }
                text += ')';
                success(text);
            }).fail(function() {
                error();
            });
        },
        gsb: function(hexDomain, success, error) {
            $.get('/api/safebrowsing/' + hexDomain, function(result) {
                if (result.issue_detected === true) {
                    success('One or more issues detected');
                }
                else {
                    success('No issues detected');
                }
            }).fail(function() {
                error();
            });
        },
        thumbnail: function(hexDomain, success, error) {
            $('#thumbnail_cancel').unbind('click').click(function() {
                $('.featherlight-close').click();
            });
            $('#thumbnail_continue').unbind('click').click(function() {
                $('#thumbnail_box .warning').hide();
                var api_path = '/api/render/' + hexDomain;
                $('#thumbnail_box img').show().attr('src', api_path);
            });
            $.featherlight('#thumbnail_box');
        }
    };

    $('.analysis_tool input.tool').click(function() {
        var $section = $(this).parent();
        var toolId = $section.data('id');
        var hexDomain = $section.data('hexdomain');
        var $destination = $section.find('.result');

        $destination.text('Checking...').fadeIn();

        toolMap[toolId](hexDomain, function(text) {
            $destination.text(text);
        }, function() {
            $destination.text('Error!');
        });

    });

});
