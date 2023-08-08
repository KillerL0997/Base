let pie = document.getElementsByTagName("footer")[0];
let cont = document.getElementsByClassName("cajaLogin");
const cajas = ["inicio","contenido","caja"];
for (let i = 0; cont[0] === undefined && i < cajas.length; i++){
    cont = document.getElementsByClassName(cajas[i]);
}
if(cont[0] != undefined && cont[0].clientWidth > document.body.clientWidth){
    document.getElementsByTagName("body")[0].style.width = "fit-content";
}
if (cont[0] != undefined && cont[0].clientHeight + pie.clientHeight >= document.body.clientHeight) {
    pie.style.position = "relative";
    pie.style.marginTop = "10px";
} else {
    pie.style.position = "fixed";
}