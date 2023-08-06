let lugar = document.getElementById('gimnasio');
let usu = document.getElementById('usuario')
lugar.onchange = function () {
    nuevo = lugar.value;
    fetch('/cambioUsuario/' + nuevo).then(function (response) {
        response.json().then(function (data) {
            let opcHTML = '';
            opcHTML += '<option value= "Nada"></option>';
            for (let i of data.lista) {
                opcHTML += '<option value="' + i.id + '"">' + i.Nombre + ' ' + i.Apellido + '</option>';
            }
            usu.innerHTML = opcHTML;
        })
    });
}