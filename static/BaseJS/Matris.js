function agregar(tipo){
    let dia = document.createElement("input");
    dia.type = 'date';
    dia.name = "Matri" + tipo;
    document.getElementById(tipo).appendChild(dia);
}
function quitar(tipo){
    let vars = document.getElementById(tipo);
    if(vars.childElementCount > 1)
        vars.removeChild(vars.lastChild);
}