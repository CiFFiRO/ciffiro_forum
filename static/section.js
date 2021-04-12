function setup_section() {
    let data_head = {'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()};
    $('#buttonExitId').on('click', function () {
    $.post("/exit/", data_head)
      .done(response => {
        window.location.replace(window.location.origin);
      }).fail(() => {
        window.location.replace(window.location.origin);
      });
    });
    $('#buttonDeleteSectionId').on('click', function () {
    let data = data_head;
    data.is_delete_section = true;
    $.post(window.location+'', data)
          .done(response => {
          if (response.ok) {
            window.location.replace(window.location.origin);
          } else {
            window.location.replace(window.location.origin);
          }
          }).fail(() => {
            window.location.replace(window.location.origin);
          });
    });
}

