$(document).ready(function() {

    // UI hooks
    $('#show_all').click(function() {
        $('.report').show();
        $('.report tr').toggleClass('displayed');
    });

    // DNS resolution
    var to_resolve = $('.resolvable').length;
    var resolvable = to_resolve;
    var found = 0;

    $('.resolved_total').text(resolvable);
    $('.resolvable').each(function() {
        var elem = $(this)

        // Detect pre-resolved IPs.
        if (elem.data('ip') !== '') {
            if (elem.data('ip') !== 'False') {
                elem.text(elem.data('ip'));
                elem.parent().addClass('resolved');
                $('.report').show();
                found += 1;
            }
            else {
                elem.text('None');
            }
            to_resolve -= 1;
            $('.resolved_count').text(resolvable - to_resolve);
            return;
        }

        // (Attempt to) resolve unresolved IPs.
        var domainb64 = elem.data('b64');
        $.getJSON('/ip/' + domainb64, function(result) {
            if (result.ip !== false) {
                elem.text(result.ip);
                elem.parent().addClass('resolved');
                $('.report').show();
                found += 1;
            }
            else if (result.error !== false) {
                elem.text('Resolution error!');
                elem.attr('title', 'There was an error resolving this IP');
                elem.parent().addClass('error');
                $('.report').show();
            }
            else {
                elem.text('None');
            }
            to_resolve -= 1;
            $('.resolved_count').text(resolvable - to_resolve);
        });
    });

    var timer = null;
    timer = setInterval(function() {
        if (to_resolve === 0) {
            clearInterval(timer);
            if (found === 0) {
                $('.progress p').text('No domains resolved');
            }
            else {
                $('.progress').hide();
            }
        }
    }, 100);
});
