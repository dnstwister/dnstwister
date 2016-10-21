$(document).ready(function() {
    $('#suggestion').click(function() {
        var $suggestion = $(this);
        $('#domains').val($suggestion.data('domain'));
        $('.error').fadeOut();
    })
});
