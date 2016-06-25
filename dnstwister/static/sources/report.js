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

    var resolveQueue = $.map($('.resolvable'), function(elem) {
        return $(elem).data('hex');
    }).reverse();

    var resolveNext = function(queue) {

        var hex = queue.pop();

        if (hex === undefined) {
            return;
        }

        $.getJSON('/api/ip/' + hex, function(result) {

            var elem = $('.resolvable[data-hex=' + hex + ']');

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

            resolveNext(queue);

        });
    };

    // 5 "threads"
    $.map([0, 1, 2, 3, 4], function() {
        setTimeout(function() {
            resolveNext(resolveQueue);
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
