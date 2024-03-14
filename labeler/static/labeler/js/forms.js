$(document).ready(function () {
    validacao();

    // Coloca o cursor no primeiro campo editavel  do form
    $(".form input:text:visible:first").not('.datepicker').focus();

    verificarAlteracoes();
});


form = $(".form");

// Variavel para verificar se foi feito o submit do form
var submitted = false;

// Define a variavel como true no submit, para não exibir o popup perguntando se deseja sair da página
form.submit(function () {
    submitted = true;
});

// Verifica se o susuário fez alterações e evisa antes de sair da página
window.addEventListener('beforeunload', (event) => {
    if (form.data("changed")) {
        // Se não foi feito o submit no form, exibe o popup perguntando se deseja sair da página
        if (!submitted) {
            event.preventDefault();
            event.returnValue = '';
        }
    }
});

// Limpa os campos do form da modal quando a mesma fecha
// $('.modal').on('hidden.bs.modal', function(){
//     $(this).find('form').trigger('reset');
// });

// Verifica se houveram alterações no form e muda a cor da linha no topo do ibox
function verificarAlteracoes() {
    $(".form :input").change(function () {

        form.data("changed", true);

        // Só muda a cor quando for edição
        if (window.location.href.includes('alterar') || window.location.href.includes('configuracoes')) {
            $(".accent-primary").removeClass('accent-primary').addClass('accent-danger')
        }

    });
}


function validacao() {

    // Sobrescrevendo as mensagens padrões
    jQuery.extend(jQuery.validator.messages, {
        required: "Campo obrigatório",
        remote: "Conserte esse campo",
        email: "Insira um E-Mail válido.",
        url: "Please enter a valid URL.",
        date: "Insira uma data válida.",
        dateISO: "Insira uma data válida (ISO).",
        number: "Insira uma número válido.",
        digits: "Insira apenas dígitos.",
        creditcard: "Insira um número de cartão válido.",
        equalTo: "Insira o mesmo valor novamente.",
        accept: "Insira um valor com uma extensão válida.",
        maxlength: jQuery.validator.format("Insira no máximo {0} caracteres."),
        minlength: jQuery.validator.format("Insira no mínimo {0} caracteres."),
        rangelength: jQuery.validator.format("Insira um valor entre {0} e {1}."),
        range: jQuery.validator.format("Insira um valor entre {0} e {1}."),
        max: jQuery.validator.format("Insira um valor igual o menor que {0}."),
        min: jQuery.validator.format("Insira um valor igual o maior que {0}.")
    });

    modal_form = $(".modal-form");


    form.validate({
        ignore: ':hidden',
        errorClass: "help-block error",

        highlight: function (element) {
            $(element).closest('.form-group').addClass('has-error');
        },
        unhighlight: function (element) {
            $(element).closest('.form-group').removeClass('has-error');
        },
        // Validando o campo quando perde o foco
        onfocusout: function (element) {
            $(element).valid();
        },
        errorPlacement: function (error, element) {

            if (element.parent('.input-group').length) {
                error.insertAfter(element.parent().parent().parent());
            } else if (element.prop('type') === 'radio' && element.parent('.radio-inline').length) {
                error.insertAfter(element.parent().parent());
            } else if (element.prop('type') === 'checkbox' || element.prop('type') === 'radio') {
                error.appendTo(element.parent().parent());
            } else if (element.prop('type') === 'select-one' || element.prop('type') === 'select-multiple') {
                error.appendTo(element.parent());
            } else {
                error.insertAfter(element);
            }
        }
    });

    modal_form.validate({

        errorClass: "help-block error",

        highlight: function (element) {
            $(element).closest('.form-group').addClass('has-error');
        },
        unhighlight: function (element) {
            $(element).closest('.form-group').removeClass('has-error');
        },
        // Validando o campo quando perde o foco
        onfocusout: function (element) {
            $(element).valid();
        }
    });

}