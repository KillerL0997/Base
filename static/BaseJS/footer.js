let pie = document.getElementsByTagName("footer")[0];
let body = (document.getElementById("contenido")) ? document.getElementById("contenido") : document.body;
if(body && body.clientWidth > document.body.clientWidth){
    document.getElementsByTagName("body")[0].style.width = "fit-content";
}
if (body && body.clientHeight + pie.clientHeight > window.screen.height) {
    pie.style.position = "relative";
    pie.style.marginTop = "10px";
} else {
    pie.style.position = "fixed";
}