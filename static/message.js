function message_page_setup(to_user_id) {
    let data = {};
    data.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
    setup_exit(data);

    let messageTextarea = $('#messageTextId');
    let messageInput = $('#messageSubjectId');
    data.message_subject = messageInput.val();

    function updateButtonState() {
      $('#sendButtonId').prop('disabled', !messageTextarea.val() || !messageInput.val());
    }
    updateButtonState();

    messageTextarea.on('input change', function () {
        data.message_text = this.value;
        updateButtonState();
    });
    messageInput.on('input change', function () {
        data.message_subject = this.value;
        updateButtonState();
    });
    $('#sendButtonId').on('click', function () {
        data.is_send_message = true;
        $.post(`/profile/${to_user_id}/`, data)
          .done(response => {
            window.location.replace(window.location.origin);
          }).fail(() => {
            window.location.replace(window.location.origin);
          });
    });
}
