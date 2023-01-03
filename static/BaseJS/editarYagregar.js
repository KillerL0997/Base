var cargo = document.getElementById("cargo_usuario");
cambio();
cargo.onchange = cambio;
var check = document.getElementById("cabeza_de_grupo");
if (check) {
  cambioBox();
  check.onchange = cambioBox;
  check.style.width = "100%";
  check.style.height = "1rem";
}
function cambioBox() {
  check = document.getElementById("cabeza_de_grupo");
  if (check.checked) {
    document.getElementById("Nombre_cabeza").style.display =
      document.getElementById("dato").style.display = "none";
    document.getElementById("dato").required = false;
  } else {
    document.getElementById("Nombre_cabeza").style.display = "block";
    document.getElementById("dato").required = true;
    document.getElementById("dato").style.display = "inline";
  }
}

function cambio() {
  if (cargo.value == "Administrador") {
    document.getElementById("dato").required = false;
    document.getElementById("cabeza_de_grupo").style.display =
      document.getElementById("cabeza").style.display =
      document.getElementById("Nombre_cabeza").style.display =
      document.getElementById("dato").style.display =
        "none";
  } else {
    check = document.getElementById("cabeza_de_grupo");
    if(check.checked){
      check.click();
    }
    check.style.display =
      document.getElementById("cabeza").style.display =
      document.getElementById("Nombre_cabeza").style.display = "block";
    document.getElementById("dato").style.display = "inline";
    document.getElementById("dato").required = true;
  }
}
