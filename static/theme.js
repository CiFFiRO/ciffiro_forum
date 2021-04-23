function theme_page_setup() {
    let csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
    let data_head = {'csrfmiddlewaretoken': csrfmiddlewaretoken,
        'is_add_post': false, 'is_delete_post': false, 'is_delete_theme': false, 'is_edit': false};
    setup_exit({'csrfmiddlewaretoken': csrfmiddlewaretoken});

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

    let editButtons = $('button[name="buttonEditPost"]');
    for (let index=0; index < editButtons.length; ++index) {
        editButtons[index].onclick = function () {
            let post_id = editButtons[index].value;
            let post_text_node = $('#removeTextId_'+post_id);
            let post_text = post_text_node.text();
            console.log(post_text);
            post_text_node.remove();
            $('#appendTextarea_'+post_id).append(
            `<textarea id="editedTextId_${post_id}" cols="50" maxlength="500">${post_text}</textarea>`
            );

            editButtons[index].onclick = function () {
                let data = data_head;
                data.is_edit_post = true;
                data.post_text = $(`#editedTextId_${post_id}`).val();
                data.post_id = post_id;
                console.log(data.post_text);
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
            }
        }
    }
}