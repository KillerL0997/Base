cambio();
document.getElementById("tipo_de_evento").onchange = cambio;
document.getElementById("gimnasio").onchange = cambio;
function cambio() {
  if (document.getElementById("tipo_de_evento").value != "Otros eventos" && document.getElementById("gimnasio").value != 'otro') {
    document.getElementById("visible").style.display = "none";
  } else {
    document.getElementById("visible").style.display = "block";
  }
}
