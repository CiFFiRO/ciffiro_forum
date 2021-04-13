function setup_login() {
    let null_field = true;
    let form = {nickname: '', password: ''};
    let errorId = 'errorId';
    let showErrorNow = false;
    form.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

    function updateButtonState() {
      $('#loginButtonId').prop('disabled', form.nickname.length === 0 || form.password.length === 0);
    }
    $('#nicknameInputId').on('input change', function () {
      form.nickname = this.value;
      updateButtonState();
    });
    $('#passwordInputId').on('input change', function () {
      form.password = this.value;
      updateButtonState();
    });
    updateButtonState();
    $('#loginButtonId').on('click', function () {
      $.post("/login/", form)
      .done(response => {
      if (response.ok) {
        Cookies.set('session_hash', response.session_hash, { sameSite: 'strict' })
        window.location.replace(window.location.origin);
      } else {
        if (!showErrorNow) {
            $('#appendErrorId').append(`
            <small id="emailHelp" class="form-text text-danger">Неверный логин или пароль.</small>
            `);
            showErrorNow = true;
        }
      }})
      .fail(() => {
      if (!showErrorNow) {
        $('#appendErrorId').append(`
         <small id="emailHelp" class="form-text text-danger">Нет ответа от сервера.</small>
        `);
        showErrorNow = true;
        }
      })
      });
}
