let imagen = document.getElementById("imgLinks");
if (imagen){
    imagen.onclick = mostrarLinks;
}

function mostrarLinks(){
    let elem = document.getElementById("links");
    if (elem){
        elem.style.left = "0";
    }
    if(elem = document.getElementById("notis")){
        elem.style.opacity = "0.5";
    }
    if(elem = document.getElementById("filtros")){
        elem.style.left = "0";
    }
    if(elem = document.getElementById("tabla")){
        elem.style.opacity = "0.5";
    }
    if(elem = document.getElementById("formFil")){
        elem.style.left = "0";
    }
    if(elem = document.getElementById("pie")){
        elem.style.opacity = "0.5";
    }
    imagen.onclick = ocultarLinks;
}
function ocultarLinks(){
    let elem = document.getElementById("links");
    if(elem){
        elem.style.left = "-50%";
    }
    if(elem = document.getElementById("notis")){
        elem.style.opacity = "1";
    }
    if(elem = document.getElementById("filtros")){
        elem.style.left = "-50%";
    }
    if(elem = document.getElementById("tabla")){
        elem.style.opacity = "1";
    }
    if(elem = document.getElementById("formFil")){
        elem.style.left = "-30%";
    }
    if(elem = document.getElementById("pie")){
        elem.style.opacity = "1";
    }
    imagen.onclick = mostrarLinks;
}