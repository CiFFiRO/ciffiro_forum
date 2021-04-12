function theme_page_setup() {
    let csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
    let data_head = {'csrfmiddlewaretoken': csrfmiddlewaretoken,
        'is_add_post': false, 'is_delete_post': false, 'is_delete_theme': false};
    $('#buttonExitId').on('click', function () {
        let data = data;
        $.post("/exit/", data)
          .done(response => {
            window.location.replace(window.location.origin);
          }).fail(() => {
            window.location.replace(window.location.origin);
          });
    });
    $('#addButtonId').on('click', function () {
        let data = data_head;
        data.is_add_post = true;
        data.post_text = $('#textInputId').val();
        $.post(window.location+'', data)
              .done(response => {
              if (response.ok) {
                location.reload();
              } else {
                window.location.replace(window.location.origin);
              }
              }).fail(() => {
                window.location.replace(window.location.origin);
              });
    });

    function updateButtonState() {
        $('#addButtonId').prop('disabled', $('#textInputId').val().length === 0);
    }
    $('#textInputId').on('input change', function () {
        updateButtonState();
    });

    if ($('#textInputId').length > 0) {
        updateButtonState();
    }

    let deleteButtons = $('button[name="buttonDeletePost"]');
    for (let index=0; index < deleteButtons.length; ++index) {
        console.log(deleteButtons[index])
        deleteButtons[index].onclick = function () {
            let data = data_head;
            data.is_delete_post = true;
            data.post_id = deleteButtons[index].value;
            $.post(window.location+'', data)
            .done(response => {
              if (response.ok) {
                location.reload();
              } else {
                window.location.replace(window.location.origin);
              }
              })
            .fail(() => {
                window.location.replace(window.location.origin);
            });
        };
    }

    $('#buttonDeleteThemeId').on('click', function () {
        let data = data_head;
        data.is_delete_theme = true;
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
    })
}