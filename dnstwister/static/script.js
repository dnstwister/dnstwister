$(document).ready(function() {
    $('.resolvable').each(function() {
        var elem = $(this)
        var domain = elem.data('domain');
        $.getJSON('/ip', {'domain': domain}, function(result) {
            if (result.ip !== null) {
                elem.text(result.ip);
            }
            else {
                elem.text('no');
            }
        });
    });
});
