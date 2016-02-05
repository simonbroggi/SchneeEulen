(function ($) {
    function setStrategy(id) {
        $.ajax({
            type: 'POST',
            url: '/api/play/'+id,
            data: '{}',
            success: function(data) {
                $('.master-strategies button').removeClass('active');
                $('button.'+id).addClass('active');
            },
            contentType: "application/json",
            dataType: 'json'
        });
    }

    function update() {
      $.getJSON( "/api/info", function(data) {
          var items = [], button;

          $('.master-strategies').children().remove();
          $.each(data.playlist, function(i, val) {
              button = $('<button type="button"/>').text(val).addClass(val + ' btn btn-default col-xs-12');
              button.click(function() {
                 setStrategy(val);
              });
              if (data['active_strategy'] == val) {
                  button.addClass('active');
              }
              $('.master-strategies').append($('<div/>').addClass('col-xs-12 col-md-3 col-sm-4').append(button).append($('<p/>').text(data['playlist_desc'][i])));
          });
        });
    }

    update();

    // periodic refresh
    setInterval(function() {
        update();
    }, 30000);

    // manual refresh
    $('.refresh').click(update);
})(jQuery);