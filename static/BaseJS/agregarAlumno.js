cambioImagen = document.getElementById("opcionFoto");
cambioImagen.onchange = seleccionFoto;
seleccionFoto();

function seleccionFoto(){
    if (cambioImagen.value == "Si"){
        document.getElementById("imagenAlumno").style.display ="inline-block";
        document.getElementById("porImagen").style.display = "block";
    }else{
        document.getElementById("imagenAlumno").style.display =
        document.getElementById("porImagen").style.display = "none";
    }
};