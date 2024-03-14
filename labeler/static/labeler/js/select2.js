$(document).ready(function () {

    iniciarSelect2()

});

function iniciarSelect2() {
    // Adicionando select2 sem busca em todos os selects que não possuem um select2 atribuido
  //  $('select').not('.select2').not('.select2_disabled').addClass('select2_sem_busca');

    // Opções globais do select2
    $.fn.select2.defaults.set("theme", "bootstrap4");

    $.fn.select2.defaults.set("width", "100%");

    $.fn.select2.defaults.set("selectOnClose", "true");

    $('.select2').select2();

    $('.select2_sem_busca').select2({
        minimumResultsForSearch: -1
    });
}

// Abre select2 on focus
$(document).on('focus', '.select2-selection.select2-selection--single', function (e) {
    $(this).closest(".select2-container").siblings('select:enabled').select2('open');
});

// Tira o focus no close
$('select.select2').on('select2:closing', function (e) {
    $(e.target).data("select2").$selection.one('focus focusin', function (e) {
        e.stopPropagation();
    });
});

function aplicarSelect2Formset() {

    setTimeout(function () {
        $('.select2_formset').select2();
    }, 200);

}