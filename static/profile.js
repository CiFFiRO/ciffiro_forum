function setup_profile() {
    let data = {};
    data.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
    setup_exit(data);

    let messageTextarea = $('#messageTextId');
    let messageInput = $('#messageSubjectId');

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

    let path = window.location.href.split('/');
    let user_id = path[path.length - 2];

    $('#sendButtonId').on('click', function () {
        data.is_send_message = true;
        $.post(`/profile/${user_id}/`, data)
          .done(response => {
            window.location.replace(window.location.origin);
          }).fail(() => {
            window.location.replace(window.location.origin);
          });
    });
    $('#banButtonId').on('click', function () {
        data.is_change_ban = true;
        $.post(`/profile/${user_id}/`, data)
          .done(response => {
            window.location.replace(window.location.href);
          }).fail(() => {
            window.location.replace(window.location.origin);
          });
    });
    $('#moderatorButtonId').on('click', function () {
        data.is_change_moderator = true;
        $.post(`/profile/${user_id}/`, data)
          .done(response => {
            window.location.replace(window.location.href);
          }).fail(() => {
            window.location.replace(window.location.origin);
          });
    });
}