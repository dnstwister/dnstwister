$(document).ready(function() {

    var toolMap = {
        parked: function(hexDomain, success, error) {
            $.get('/api/parked/' + hexDomain, function(result) {
                var scorePercent = Math.round(result.score * 100);
                var text = result.score_text + ' (' + scorePercent + ' %';
                if (result.redirects === true and result.dressed !== true) {
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
        whois: function(hexDomain, success, error) {
            $.get('/api/whois/' + hexDomain, function(result) {
                success(result.whois_text);
            }).fail(function() {
                error();
            });
        }
    };

    // Generic tools.
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

    // Whois
    $('#whois_lookup').click(function() {
        var $this = $(this);
        var hexDomain = $this.data('hexdomain');
        var $section = $this.parent();
        var $destination = $section.find('.result');
        $destination.text('Querying...').fadeIn();

        toolMap['whois'](hexDomain, function(text) {
            $destination.text(text);
        }, function() {
            $destination.text('Unable to retrieve WHOIS data.');
        });
    });

});
