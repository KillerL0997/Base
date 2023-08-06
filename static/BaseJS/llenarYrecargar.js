function llenar(tipo, opc, modo, msj) {
  var cajas = document.getElementsByName("checkbox");
  var lim = cajas.length;
  var ids = "";
  var tams = "";
  for (var i = 0; i < lim; i++) {
    while (i < lim && cajas[i].checked) {
      var cont = 1;
      var valor = cajas[i].value;
      while ((valor = parseInt(valor / 10)) > 0) {
        cont++;
      }
      tams += String(cont);
      ids += String(cajas[i].value);
      i++;
    }
  }
  if (ids) {
    if (tipo == "Matriculas") {
      location.href = "/crear/" + opc + "/" + ids + "/" + tams;
      return;
    }
    if (tipo == "Gims") {
      if(opc == "DesaGims"){
        if (msj == "Administrador") {
          location.href = "/eliminar_gimnasio/" + ids + "/" + tams + "/" + modo;
          return;
        } else {
          location.href = "/desaGim/" + ids + "/" + tams;
          return;
        }
      }
      if(opc == "HabiGims"){
        document.location.assign("/habiGims/" + ids + "/" + tams);
        return;
      }
      if(opc == "ElimGims"){
        location.href = "/elimGim/" + ids + "/" + tams;
        return;
      }
    }
    if(tipo == "Alumnos"){
      if(opc == "Desa"){
        location.href = "/desaAlum/" + ids + "/" + tams;
        return;
      }
      if(opc == "Examen" || opc == "Torneo"){
        location.href = "/sumarAevento/" + ids + "/" + tams + "/" + opc;
        return;
      }
      if(opc == "Elim"){
        location.href = "/elimAlus/" + ids + "/" + tams;
        return;
      }
      if(opc == "Habi"){
        document.location.assign("/habiAlums/" + ids + "/" + tams);
        return;
      }
      if(opc == "libre"){
        location.href = "/libretas/" + ids + "/" + tams;
        return; 
      }
    }
  }
}
