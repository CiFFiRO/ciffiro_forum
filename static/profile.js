function setup_profile() {
    setup_exit();
    let data = {};
    data.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
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
    $('#sendButtonId').on('click', function () {
        let path = window.location.href.split('/');
        data.is_send_message = true;
        $.post(`/profile/${path[path.length - 2]}/`, data)
          .done(response => {
            window.location.replace(window.location.origin);
          }).fail(() => {
            window.location.replace(window.location.origin);
          });
    });
}