const tipoMatri = ["AATEE","FETRA","ENAT"];
function agregar() {
    let cont = document.getElementById("contMaris");
    let dato = document.createElement("section");
    dato.className = "datos";
    dato.innerHTML = "<section class='datosMatri'><label for=''>Fecha</label>" +
        "<input type='date' name='fecha' id=''></section><section class='datosMatri'>" +
        "<label for=''>Tipo</label><select name='tipoMatri' id=''><option value='AATEE'>AATEE</option>" +
        "<option value='FETRA'>Fetra</option><option value='ENAT'>Enat</option></select></section>";
    cont.insertAdjacentElement("beforeend", dato);
}
function eliminar() {
    let cont = document.getElementById("contMaris");
    if (cont.childElementCount > 1) {
        cont.removeChild(cont.lastChild);
    }
}
function matris(idAlu, modo){
    let vecMatris = [];
    switch(modo){
        case 'agregar':
            var fechas = document.getElementsByName("fecha");
            var tipos = document.getElementsByName("tipoMatri");
            for(var i = 0; i < tipos.length; i++){
                if(fechas[i].value){
                    vecMatris.push({fecha: fechas[i].value, tipo: tipos[i].value});
                }
            }
            tipoMatri.forEach((elem) => {
                var vec = filtroFechas(vecMatris.filter(({fecha,tipo}) => {
                    return tipo == elem;
                }).map(({fecha,tipo}) => {
                    return fecha;
                }))
                if (vec){
                    fetch("/agregaMatris/" + vec + "/" + elem + "/" + idAlu);
                }
            });
            break;
        case 'editar':
            var fechas = document.getElementsByName("fecha");
            var check = document.getElementsByName("selec");
            var ids = document.getElementsByName("idMatri");
            for(let i = 0; i < check.length; i++){
                if (check[i].checked){
                    vecMatris.push({id: ids[i].value, fecha: fechas[i].value});
                }
            }
            if(vecMatris){
                fetch("/editaMatris/" + cadIds(vecMatris.map((obj) => {
                    return obj.id;
                })) + "/" + cadFechas(vecMatris.map((obj) => {
                    return obj.fecha;
                })) + "/" + document.getElementById("tipo").innerHTML + "/" + idAlu);
            }
            break;
        case 'eliminar':
            var check = document.getElementsByName("selec");
            var ids = document.getElementsByName("idMatri");
            for(let i = 0; i < check.length; i++){
                if (check[i].checked){
                    vecMatris.push(ids[i].value);
                }
            }
            if (vecMatris){
                fetch("/elimMatris/" + cadIds(vecMatris));
            }
            break;
    }
    document.location.replace('/ver_alumnos/habilitado');
}
function filtroFechas(vecTemp){
    for(let i = 0; i < vecTemp.length; i++){
        for(let j = i + 1; j < vecTemp.length; j++){
            if(vecTemp[i] == vecTemp[j]){
                vecTemp.splice(j,1);
                j--;
            }
        }
    }
    return cadFechas(vecTemp);
}
function cadFechas(fechas){
    var cad = "";
    fechas.forEach((elem) => {
        cad += elem + "n";
    });
    return cad.substring(0,cad.length - 1);
}
function cadIds(ids){
    var cad = "";
    ids.forEach((elem) => {
        cad += elem + "n";
    });
    return cad.substring(0, cad.length - 1);
}