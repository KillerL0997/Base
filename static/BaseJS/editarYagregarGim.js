var botonSuma = document.getElementById("Sumar");
botonSuma.onclick = sumar;

var botonResta = document.getElementById("Restar");
botonResta.onclick = restar;

var horarios = 0;

var id = document.getElementsByName("oculto")[0].value;

function sumar(){
    var lugar = document.getElementsByClassName("divHorarios");
    if(lugar.length == 0){
        lugar = document.getElementsByTagName("table");
        if(lugar.length == 0){
            lugar = document.getElementsByName("oculto");
        }
    }
    var div = document.createElement("div");
    div.className = "divHorario";
    var nuevo = document.createElement("input");
    nuevo.id = "horariosGimnasio";
    nuevo.name = "horariosGimnasio";
    nuevo.size = 30;
    nuevo.type = "text";
    div.insertAdjacentElement("afterbegin",nuevo);
    var nuevo = document.createElement("select");
    nuevo.id = "usuarios";
    nuevo.name = "usuarios"
    fetch("/instructores/" + id).then(function(response){
        response.json().then(function(data){
            let opc = "";
            for(let i of data.lista){
                opc += '<option value="' + i.id + '">' + i.nya + '</option>';
            }
            nuevo.innerHTML += opc;
        });
    });
    div.insertAdjacentElement("beforeend",nuevo);
    lugar[0].insertAdjacentElement("afterend",div);
    horarios++;
    botonResta.disabled = false;
}
function restar(){
    var borrar = document.getElementsByClassName("divHorario");
    borrar[horarios - 1].remove();
    horarios--;
    if (horarios == 0){
        botonResta.disabled = true;
    }
}