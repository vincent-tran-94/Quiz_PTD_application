$(document).ready(function() {
    $('.star').on('mouseover', function() {
        var rating = parseInt($(this).attr('data-rating'));
        $('.star').each(function() {
            if (parseInt($(this).attr('data-rating')) <= rating) {
                $(this).addClass('active');
            } else {
                $(this).removeClass('active');
            }
        });
    });

    $('.star').on('click', function() {
        var rating = parseInt($(this).attr('data-rating'));
        $('#thank-you-message').show();
        $('.star').each(function() {
            if (parseInt($(this).attr('data-rating')) <= rating) {
                $(this).addClass('selected');
            } else {
                $(this).removeClass('selected');
            }
        });
    });
});