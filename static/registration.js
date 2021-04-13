function setup_registration() {
    let form = {email: '', nickname: '', password: ''};
    form.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

    function updateButtonState() {
      $('#registrationButtonId').prop('disabled', !Validator.registrationForm(form) ||
      form.password != $('#passwordRetryInputId').val());
    }
    updateButtonState();

    function updateInputStatus(id, validator, value) {
      let obj = $(`#${id}`);
      if (!validator(value)) {
        obj.addClass('is-invalid');
      } else {
        obj.removeClass('is-invalid');
      }
    }

    $('#nicknameInputId').on('input change', function () {
      form.nickname = this.value;
      updateInputStatus('nicknameInputId', Validator.nickname, this.value);
      updateButtonState();
    });
    $('#emailInputId').on('input change', function () {
      form.email = this.value;
      updateInputStatus('emailInputId', Validator.email, this.value);
      updateButtonState();
    });
    $('#passwordInputId').on('input change', function () {
      form.password = this.value;
      updateInputStatus('passwordInputId', Validator.password, this.value);
      updateButtonState();
    });
    $('#passwordRetryInputId').on('input change', function () {
      updateInputStatus('passwordRetryInputId', (password) => {
        return password === $('#passwordInputId').val();
      }, this.value);
      updateButtonState();
    });

    $('#registrationButtonId').on('click', function () {
        $.post("/registration/", form)
          .done(response => {
          if (response.ok) {
            window.location.replace(window.location.origin);
          } else {
             $('#serverMessage').text(response.message);
          }
          }).fail(() => {
            window.location.replace(window.location.origin);
          });
    });
}
