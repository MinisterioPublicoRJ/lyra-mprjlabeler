$('.confirm_delete').on('click', function (e) {
    e.preventDefault();

    var texto = $(this).data('texto-extra');
    var titulo = $(this).data('titulo');

    if(!titulo){
        titulo = 'Tem certeza que deseja excluir?';
    }

    Swal.fire({
        title: titulo,
        text: texto,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sim',
        cancelButtonText: 'Não'
    }).then((result) => {
        if (result.value) {
            window.location.href = e.currentTarget.href;
        }
    })


});