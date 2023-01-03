let imagen = document.getElementById("imgLinks");
if (imagen){
    imagen.onclick = mostrarLinks;
}

function mostrarLinks(){
    document.getElementById("links").style.left = "0";
    imagen.onclick = ocultarLinks;
}
function ocultarLinks(){
    document.getElementById("links").style.left = "-40%";
    imagen.onclick = mostrarLinks;
    ocultarSubmenu();
}
function mostrarSubmenu(nom){
    ocultarSubmenu();
    let ul = document.getElementById(nom);
    ul.style.display = "block";
}
function ocultarSubmenu(){
    let submenu = document.getElementsByClassName("submenu");
    for (let i = 0; i < submenu.length; i++){
        submenu[i].style.display = "none";
    }
}