function setup_exit(data) {
    $('#buttonExitId').on('click', function () {
        $.post("/exit/", data)
          .done(response => {
            window.location.replace(window.location.origin);
          }).fail(() => {
            window.location.replace(window.location.origin);
          });
    });
}



