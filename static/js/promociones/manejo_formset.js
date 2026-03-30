document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('productos-container');
    const totalForms = document.getElementById('id_detallepromocion_set-TOTAL_FORMS');
    const emptyTemplate = document.getElementById('empty-form-template').innerHTML;
    let formIdx = parseInt(totalForms.value);

    document.getElementById('add-producto').addEventListener('click', function () {
      let newForm = emptyTemplate
        .replace(/__producto__/g, document.querySelector('#productos-container .producto-form').querySelector('select').outerHTML.replace(/-\d+-/g, `-${formIdx}-`))
        .replace(/__cantidad__/g, document.querySelector('#productos-container .producto-form').querySelector('input[type=number]').outerHTML.replace(/-\d+-/g, `-${formIdx}-`))
        .replace(/__delete__/g, `<input type="hidden" name="detallepromocion_set-${formIdx}-DELETE" id="id_detallepromocion_set-${formIdx}-DELETE">`);

      const wrapper = document.createElement('div');
      wrapper.innerHTML = newForm;
      container.appendChild(wrapper);

      formIdx++;
      totalForms.value = formIdx;
    });

    container.addEventListener('click', function (e) {
        const botonEliminar = e.target.closest('.remove-producto');
        if (botonEliminar) {
        botonEliminar.closest('.producto-form').remove();
        formIdx--;
        totalForms.value = formIdx;
        }
    });
  });