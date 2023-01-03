var contra = document.getElementById("Contra");
contra.onclick = mostrar;
function mostrar() {
    fetch("/contra/" + contra.value).then(function(response){
        response.json().then(function(dato){
            alert(dato.lista.msj);
        });
    });
}
