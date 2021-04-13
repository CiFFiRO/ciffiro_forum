function setup_add_section_theme(path_request) {
    let form = {name: ''};
    let showErrorNow = false;
    form.csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();

    function updateButtonState() {
    $('#addButtonId').prop('disabled', form.name.length === 0);
    }
    $('#nameInputId').on('input change', function () {
    form.name = this.value;
    updateButtonState();
    });
    updateButtonState();

    $('#addButtonId').on('click', function () {
      $.post(path_request, form)
      .done(response => {
      if (response.ok) {
        window.location.replace(window.location.origin);
      } else {
        if (!showErrorNow) {
            $('#appendErrorId').append(`
            <small id="emailHelp" class="form-text text-danger">Недопустимое название.</small>
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
