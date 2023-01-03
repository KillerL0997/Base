var botonSuma = document.getElementById("Sumar");
botonSuma.onclick = sumar;

var botonResta = document.getElementById("Restar");
botonResta.onclick = restar;

var horarios = 0;

var id = document.getElementsByName("oculto")[0].value;

function sumar(){
    var lugar = document.getElementsByName("usuarios");
    var nuevo = document.createElement("input");
    nuevo.id = "horariosGimnasio";
    nuevo.name = "horariosGimnasio";
    nuevo.size = 30;
    nuevo.type = "text";
    if (lugar.length != 0){
        lugar[horarios - 1].insertAdjacentElement("afterend",nuevo);
    }else{
        var lugar = document.getElementsByName("oculto");
        lugar[0].insertAdjacentElement("afterend",nuevo);
    }
    horarios += 1;
    lugar = document.getElementsByName("horariosGimnasio");
    var nuevo = document.createElement("select");
    nuevo.id = "usuarios";
    nuevo.name = "usuarios"
    if(horarios == 0){
        lugar[0].insertAdjacentElement("afterend",nuevo);
    }else{
        lugar[horarios - 1].insertAdjacentElement("afterend",nuevo);
    }
    fetch("/instructores/" + id).then(function(response){
        response.json().then(function(data){
            let opc = "";
            for(let i of data.lista){
                opc += '<option value="' + i.id + '">' + i.nya + '</option>';
            }
            nuevo.innerHTML += opc;
        });
    });
    botonResta.disabled = false;
}
function restar(){
    var nuevo = document.getElementsByName("usuarios");
    if(horarios == 0){
        nuevo[0].remove();
    } else{
        nuevo[horarios - 1].remove();
    }
    var nuevo = document.getElementsByName("horariosGimnasio");
    if(horarios == 0){
        nuevo[0].remove();
    } else{
        nuevo[horarios - 1].remove();
        horarios -= 1;
    }
    if (horarios == 0){
        botonResta.disabled = true;
    }
}