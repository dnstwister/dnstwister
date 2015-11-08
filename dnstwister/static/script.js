$(document).ready(function() {
    var count = $('.resolvable').length;
    var found = 0;
    $('.resolvable').each(function() {
        var elem = $(this)
        var domain = elem.data('domain');
        $.getJSON('/ip', {'domain': domain}, function(result) {
            if (result.ip !== null) {
                elem.text(result.ip);
                elem.parent().show();
                found += 1;
            }
            count -= 1;
        });
    });

    var timer = null;
    timer = setInterval(function() {
        if (count === 0) {
            clearInterval(timer);
            if (found === 0) {
                $('.progress td').text('No domains resolved');
            }
            else {
                $('.progress').hide();
            }
        }
    }, 100);
});
