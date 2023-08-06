var cargo = document.getElementById("cargo_usuario");
cambio();
cargo.onchange = cambio;
function cambio() {
  if (cargo.value == "Administrador" || cargo.value == "Cabeza") {
    document.getElementById("cabeza").required = false;
    document.getElementById("Nombre_cabeza").style.display =
      document.getElementById("cabeza").style.display =
      document.getElementById("instructor").style.display =
      document.getElementById("porInstructor").style.display =
        "none";
  } else{
    document.getElementById("cabeza").required = true;
    document.getElementById("Nombre_cabeza").style.display =
    document.getElementById("porInstructor").style.display = "block";
    document.getElementById("cabeza").style.display =
    document.getElementById("instructor").style.display = "inline";
  }
}
