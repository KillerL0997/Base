cambioTipo();
cambioLugar();
document.getElementById("tipo_de_evento").onchange = cambioTipo;
document.getElementById("gimnasio").onchange = cambioLugar;
function cambioLugar() {
  if (document.getElementById("gimnasio").value != 'otro') {
    document.getElementById("lugar").style.display = "none";
  } else {
    document.getElementById("lugar").style.display = "flex";
  }
}
function cambioTipo() {
  if (document.getElementById("tipo_de_evento").value != "Otros eventos") {
    document.getElementById("tipo").style.display = "none";
  } else {
    document.getElementById("tipo").style.display = "flex";
  }
}
