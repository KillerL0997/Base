function verUsuarios(cargo, instru) {
    fetch("/filtroUsuario/" + cargo + "/" + instru).then(function (response) {
        response.json().then(function (data) {
            let text = "<table border='1' id='tabla'>";
            let lim = data['ids'].length;
            if (lim == 0) {
                text += "<thead><tr><th colspan='2'>No se encontraron datos</th></tr></thead><tbody>";
            } else {
                text += "<thead><tr><th>Usuario</th><th>Cargo</th><th></th></tr></thead><tbody>";
                for (let i = 0; i < lim; i++) {
                    text += "<tr>"
                        + "<td><a onclick='mostrarDato()'>" + data['apes'][i] + " " + data['noms'][i]
                        + "</a></td><td>" + data['cargos'][i] + "</td>"
                        + "<td><a href='/eliminar_usuario/" + data['ids'][i] + "'><img"
                        + " src='../../../static/CSS/icons8-eliminar-50.png' alt='Eliminar'></a></td>"
                        + "</tr>";
                }
                text += "</tbody></table>";
            }
            document.getElementById("tabla").innerHTML = text;
        });
    });
}

function verGimnasio(modo) {
    fetch("/filtroGim/" + document.getElementById("usuario").value + "/" + modo).then(function (response) {
        response.json().then(function (data) {
            let text = "<table border='1' id='tabla'>";
            let lim = data['ids'].length;
            if (lim == 0) {
                text += "<thead><tr><th colspan = '2'>Sin gimnasios asociados</th></tr></thead><tbody>";
            } else {
                text += "<thead><tr><th></th><th>Nombre</th><th>Direccion</th></thead><tbody>";
                for (let i = 0; i < lim; i++) {
                    text += "<tr><td><input type='checkbox' name='checkbox' value=" + data['ids'][i]
                        + "></td><td><a onclick=mostrarDato(" + data['ids'][i] + ",'gim')>"
                        + data['noms'][i] + "</a></td><td>" + data['direc'][i] + "</td></tr>";
                }
            }
            text += "</tbody></table>";
            document.getElementById("tabla").innerHTML = text;
        });
    });
    let text = "<button class='btnFilRedondeado' type='button' onclick=verGimnasio(";
    if (modo == 'deshabilitado') {
        text += "'habilitado')>Ver habilitados</button>";
    } else {
        text += "'deshabilitado')>Ver deshabilitados</button>";
    }
    document.getElementsByTagName("button")[3].outerHTML = text;
}

function verEventos(tipo, usu) {
    let fDesde = (document.getElementsByName("fDesde")[0].value) ? document.getElementsByName("fDesde")[0].value : "_";
    let fHasta = (document.getElementsByName("fHasta")[0].value) ? document.getElementsByName("fHasta")[0].value : "_";
    fetch("/filtroEvento/" + fDesde + "/" + fHasta + "/" + tipo).then(function (response) {
        response.json().then(function (data) {
            let text = "<h2>" + tipo + "</h2><table border='1' id='tabla'>";
            let lim = data['ids'].length;
            if(lim == 0){
                text += "<thead><tr><th colspan = '2'>Sin resultados</th></tr></thead><tbody>";
            } else {
                if (usu == 'Administrador'){
                    text += "<thead><tr><th>Fecha</th><th></th></tr></thead><tbody>";
                    for(let i = 0; i < lim; i++){
                        text += "<tr><td><a onclick=mostrarDato(" + data['ids'][i] + ",'eve')>"
                        + data['fechas'][i] + "</a></td><td>"
                        + "<a href=/eliminar_evento/" + data['ids'][i] 
                        + "><img src='../../../static/CSS/icons8-eliminar-50.png' alt='Eliminar'></a>"
                        + "</td></tr>";
                    }
                } else {
                    text += "<thead><tr><th>Fecha</th></tr></thead><tbody>";
                    for(let i = 0; i < lim; i++){
                        text += "<tr><td>" + data['fechas'][i] +"</td></tr>";
                    }
                }
            }
            text += "</tbody></table>";
            document.getElementById("tabla").innerHTML = text;
        });
    });
}

function cambioTipoEvento(tipo, usu) {
    document.getElementsByName("fDesde")[0].value =
        document.getElementsByName("fHasta")[0].value = "";
    document.getElementsByTagName("button")[1].outerHTML = "<button class='btnFilRedondeado'"
    + " onclick=verEventos('" + tipo + "','" + usu + "')>Aceptar</button>";
    verEventos(tipo, usu);
}

// Recibe los filtros
function verAlumnos(cargo){
    nom = (document.getElementById("Nombre").value) ? document.getElementById("Nombre").value : "_";
    ape = (document.getElementById("Apellido").value) ? document.getElementById("Apellido").value : "_";
    cate = (document.getElementById("usuario").value) ? document.getElementById("usuario").value : "_";
    gim = (document.getElementById("gimnasio").value) ? document.getElementById("gimnasio").value : 0;
    instru = (
        document.getElementById("dato") &&
        document.getElementById("dato").value
        ) ? document.getElementById("dato").value : 0;
    fAatee = (
        document.getElementById("fAatee") &&
        document.getElementById("fAatee").value
        ) ? document.getElementById("fAatee").value : "_";
    fEnat = (
        document.getElementById("fEnat") &&
        document.getElementById("fEnat").value
        ) ? document.getElementById("fEnat").value : "_";
    fFetra = (
        document.getElementById("fFetra") &&
        document.getElementById("fFetra").value
        ) ? document.getElementById("fFetra").value : "_";
    fetch("/filtroAlumno/" + nom + "/" + ape + "/" + cate + "/" + gim + "/" + instru + "/" +
    fAatee + "/" + fEnat + "/" + fFetra).then(function(response){
        response.json().then(function(data){
            let text = "<table border='1' id='tabla'>";
            lim = data['ids'].length
            if (lim == 0){
                if (cargo == "Administrador"){
                    text += "<thead><tr><th colspan = '7'>Sin resultados</th></tr></thead><tbody>";
                } else {
                    text += "<thead><tr><th colspan = '4'>Sin resultados</th></tr></thead><tbody>";
                }
            } else {
                if (cargo == "Administrador"){
                    text += "<thead><tr><th></th><th>Ult. examen</th>" +
                    "<th>Apellido y Nombre</th><th>Categoria</th><th>AATEE</th><th>Fetra</th>" +
                    "<th>Enat</th></tr></thead>";
                    for(let i = 0; i < lim; i++){
                        text += "<tr><td><input type='checkbox' name='checkbox' value=" + 
                        data['ids'][i] + "></td><td>" + data['uExas'][i] +
                        "</td><td class= '" + data['libres'][i] +
                        "'><a onclick=mostrarDato('" + data['ids'][i] + "','alu','" + cargo +
                        "')>" + data['apes'][i] + " " + data['noms'][i] +
                        "</a></td><td>" + data['cates'][i] + "</td><td>" + data['fAatees'][i] +
                        "</td><td>" + data['fFetras'][i] + "</td><td>" + data['fEnats'][i] +
                        "</td></tr>";
                    }
                } else {
                    text += "<thead><tr><th></th><th>Ult. examen</th>" +
                    "<th>Apellido y Nombre</th><th>Categoria</th></tr></thead>";
                    for(let i = 0; i < lim; i++){
                        text += "<tr><td><input type='checkbox' name='checkbox' value=" + 
                        data['ids'][i] + "></td><td>" + data['uExas'][i] +
                        "</td><td class= '" + data['libres'][i] +
                        "'><a onclick=mostrarDato('" + data['ids'][i] + "','alu','" + cargo +
                        "')>" + data['apes'][i] + " " + data['noms'][i] +
                        "</a></td><td>" + data['cates'][i] + "</td></tr>";
                    }
                }
            }
            text += "</tbody></table>";
            document.getElementById("tabla").outerHTML = text;
        });
    });
}

function asignarMatris(tipo){
    chechs = document.getElementsByName("checkbox");
    text = "";
    chechs.forEach((elem) => {
        if(elem.checked){
            text += elem.value + "n";
        }
    });
    fetch("/asignarMatris/" + tipo + "/" + text.substring(0, text.length - 1));
    window.location.reload()
}