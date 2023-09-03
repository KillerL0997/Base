let lugar = document.getElementById("gimnasio");
let usu = document.getElementById("dato");
let caja = document.getElementById("cont");
let mostrar = document.getElementById("info");
let extra = document.getElementById("extra");
let eventos = ["Alumno", "Examen", "Torneo", "Otros eventos"];
let alus = [];
let fechas = [];
let lugares = [];
let direcciones = [];

if (lugar) {
  lugar.onchange = function () {
    nuevo = (lugar.value) ? lugar.value : "Nada";
    fetch("/cambioUsuario/" + nuevo).then(function (response) {
        response.json().then(function (data) {
          let opcHTML = "";
          opcHTML += '<option value= ""></option>';
          for (let i of data.lista) {
            opcHTML +=
              '<option value="' +
              i.id +
              '">' +
              i.Nombre +
              " " +
              i.Apellido +
              "</option>";
          }
          usu.innerHTML = opcHTML;
        });
      });
  };
}

function mostrarDato(id, tipo, opc) {
  switch (tipo) {
    case "usu":
      mostrarUsu(id);
      footerCaja(263);
      break;
    case "gim":
      mostrarGim(id);
      footerCaja(777);
      break;
    case "alu":
      mostrarAlu(id, opc);
      footerCaja(671);
      break;
    case "eve":
      mostrarEven(id);
      footerCaja(307)
      break;
  }
}

function mostrarAlu(idAlu, tipoUsu) {
  fetch("/mostrarAlu/" + idAlu).then(function (response) {
    response.json().then(function (data) {
      mostrar.innerHTML = extra.innerHTML = "";
      for (let alu in data.lista) {
        if (data.lista[alu]) {
          let elem = document.createElement("p");
          elem.innerHTML = data.mensajes[alu] + data.lista[alu];
          mostrar.insertAdjacentElement("beforeend", elem);
        }
      }
      let estados = [true];
      for (let elem of data.botones) {
        estados.push(elem);
      }
      let imagen = document.createElement("img");
      imagen.src = data.foto.slice(5, data.foto.lenght);
      extra.insertAdjacentElement("beforeend", imagen);
      mostrar.innerHTML += crearBotones(eventos, "Alumno", idAlu, estados, tipoUsu);
      if (tipoUsu == 'Administrador') {
        mostrar.innerHTML += "<div class='dosBotones'><button class='btnRedondeado'"
          + "onclick= location.href='/editar_alumno/" + idAlu + "'>Editar</button>" +
          "<button class='btnRedondeado' onclick=aluMatris(" + idAlu + ",'" + tipoUsu + "')>Matriculas</button></div>";
      } else {
        mostrar.innerHTML += "<button class='btnRedondeado' style='width: 60%;'" +
          " onclick=location.href ='/editar_alumno/" + idAlu + "'>Editar</button>";
      }
      caja.style.display = "flex";
      mostrar.style.display = "block";
      extra.style.display = "flex";
    });
  });
}

function aluMatris(idAlu, tipoUsu) {
  fetch("/aluMatris/" + idAlu).then(function (response) {
    response.json().then(function (data) {
      mostrar.innerHTML = "<h3>Fetra</h3><p>" + data.fFetra
        + "</p><h3>AATEE</h3><p>" + data.fAatee
        + "</p><h3>Enat</h3><p>" + data.fEnat
        + "</p><div class= 'tresBotones'><button class='btnRedondeado' onclick= matrisAlu("
        + idAlu + ",'FETRA','" + tipoUsu +"')>Fetra</button><button class='btnRedondeado' onclick= matrisAlu("
        + idAlu + ",'AATEE','" + tipoUsu +"')>AATEE</button><button class='btnRedondeado' onclick= matrisAlu("
        + idAlu + ",'ENAT','" + tipoUsu +"')>Enat</button></div><div class='dosBotones'>" +
        "<button class='btnRedondeado' onclick=modiMatris(" + idAlu + ",'todo','agregar')>" +
        "Agregar</button><button class='btnRedondeado' onclick = mostrarAlu("
        + idAlu + ",'" + tipoUsu + "')>Regresar</button></div>";
    });
  });
}

function matrisAlu(idAlu, tipo, tipoUsu) {
  fetch("/matrisAlu/" + idAlu + "/" + tipo).then(function (response) {
    response.json().then(function (data) {
      let text = "<h3>Fechas de matriculas " + tipo + "</h3>";
      for (let elem of data.matris) {
        text += "<p>" + elem + "</p>";
      }
      text += "<div class='dosBotones'><button class='btnRedondeado' onclick=modiMatris("
        + idAlu + ",'" + tipo + "','editar')>Editar</button><button class='btnRedondeado' onclick=modiMatris("
        + idAlu + ",'" + tipo + "','eliminar')>Eliminar</button></div><button class='btnRedondeado' style='width: 60%;' onclick=aluMatris("
        + idAlu + ",'" + tipoUsu + "')>Regresar</button>";
      mostrar.innerHTML = text;

    });
  });
}

function modiMatris(idAlu, tipo, modo) {
  location.href = "/modiMatris/" + idAlu + "/" + tipo + "/" + modo;
}

function eventosAlu(idAlu, tipo, estado, tipoUsu) {
  fetch("/eventosAlu/" + idAlu + "/" + tipo).then(function (response) {
    response.json().then(function (data) {
      fechas = data.fechas;
      lugares = data.lugares;
      mostrar.innerHTML = mostrarEventos(0, 10, fechas.length, tipo)
        + crearBotones(eventos, tipo, idAlu, estado, tipoUsu);
    });
  });
}

function mostrarEventos(ini, lim, top, tipo) {
  let text = "<h2>" + tipo + "</h2><div class='divEventos'>";
  for (let pos = ini; pos < lim && pos < top; pos++) {
    text += "<p style= 'width: 50%;'>" + fechas[pos] + ":</p><p>" + lugares[pos] + "</p>";
  }
  text += "</div>";
  text += "<div class='dosBotones'><button class='btnRedondeado' onclick= mostrarEventos(" +
    (ini - 10) + "," + ini + "," + top + "," + tipo + ")";
  if (ini == 0) {
    text += " disabled";
  }
  text += ">Anterior</button><button class='btnRedondeado' onclick= mostrarEventos(" +
    lim + "," + (lim + 10) + "," + top + "," + tipo + ")";
  if (lim >= top) {
    text += " disabled";
  }
  text += ">Siguiente</button></div>";
  return text;
}

function crearBotones(lista, filtro, idAlu, desa, tipoUsu) {
  let text = "<div class='tresBotones'>";
  for (let pos in lista) {
    if (lista[pos] != filtro) {
      if (lista[pos] == "Alumno") {
        text += "<button class='btnRedondeado' onclick = mostrarAlu("
          + idAlu + ",'" + tipoUsu + "')";
      } else {
        text += "<button class='btnRedondeado' onclick = eventosAlu("
          + idAlu + ",'" + lista[pos] + "',[" + desa + "],'" + tipoUsu + "')";
      }
      if (!desa[pos]) {
        text += " disabled";
      }
      text += ">" + lista[pos] + "</button>";
    }
  }
  return text + "</div>";
}

function mostrarGim(idGim) {
  fetch("/mostrarGim/" + idGim).then(function (response) {
    response.json().then(function (data) {
      let text = "<p>Nombre: " + data.gimnasio[0] + "</p><p>Direccion: " +
        data.gimnasio[1] + "</p><h3>Instructores</h3>";
      for (let elem of data.usuarios) {
        text += "<p>" + elem + "</p>";
      }
      text += "<img src = '/static/" + data.gimnasio[2] + "'>"
        + "<button class='btnRedondeado' style='width: 60%'"
        + " onclick= location.href='/editar_gimnasio/" + idGim + "'>Editar</button>";
      mostrar.innerHTML = text;
      alus = data.alumnos;
      mostrarAlus(0, 11, alus.length);
      caja.style.marginTop = "5%";
      caja.style.display = "flex";
    });
  });
}

function mostrarAlus(ini, lim, top) {
  let text = "<h2>Alumnos</h2>";
  for (let pos = ini; pos < lim && pos < top; pos++) {
    text += "<p>" + alus[pos] + "</p>";
  }
  text += "<div class='dosBotones'><button class='btnRedondeado' onclick=mostrarAlus("
    + (ini - 11) + "," + ini + "," + top + ")";
  if (ini <= 0) {
    text += " disabled";
  }
  text += ">Anterior</button><button class='btnRedondeado' onclick=mostrarAlus("
    + lim + "," + (lim + 11) + "," + top + ")";
  if (lim >= top) {
    text += " disabled";
  }
  text += ">Siguiente</button></div>";
  extra.innerHTML = text;
}

function mostrarUsu(idUsu) {
  fetch("/mostrarUsu/" + idUsu).then(function (response) {
    response.json().then(function (data) {
      mostrar.innerHTML = "<p>Nombre: " + data.usuario[0] + " " + data.usuario[1]
        + "</p><p>Documento: " + data.usuario[2] + "</p><p>Email: " + data.usuario[3]
        + "</p><p>Categoria: " + data.usuario[4] + "</p><p>Cargo: " + data.usuario[5]
        + "</p><p>Instructor: " + data.instructor + "</p><p>Cabeza de grupo: "
        + data.cabeza + "</p>";
      direcciones = data.dirGims;
      lugares = data.nomGims;
      let text = "<div class='botonUsuario'><button class='btnRedondeado' onclick= mostrarGimsUsu("
        + idUsu + ")";
      if (!data.dirGims) {
        text += " disabled";
      }
      text += ">Gimnasios</button><button class='btnRedondeado' onclick= contraUsu("
        + idUsu + ")>Contraseña</button></div><button class='btnRedondeado'"
        + " style='width: 60%;' onclick=location.href='/editar_usuario/" + idUsu
        + "/editar'>Editar</button>";
      extra.innerHTML = text;
      caja.style.display = "flex";
    });
  });
}

function mostrarGimsUsu(idUsu) {
  let text = "";
  for (let pos in lugares) {
    text += "<p>" + lugares[pos] + "</p><p>" + direcciones[pos] + "</p>";
  }
  text += "<div class='botonUsuario'><button class='btnRedondeado' onclick= mostrarUsu("
    + idUsu + ")>Regresar</button>"
  extra.style.flexDirection = "column";
  extra.innerHTML = text;
}

function contraUsu(idUsu) {
  fetch("/contraUsu/" + idUsu).then(function (response) {
    response.json().then(function (data) {
      let text = "<p>Contraseña: " + data.contra
        + "</p><div class='botonUsuario'><button class='btnRedondeado' onclick= mostrarUsu("
        + idUsu + ")>Regresar</button></div>";
      extra.style.flexDirection = "column";
      extra.innerHTML = text;
    });
  });
}

function mostrarEven(idEven) {
  fetch("/mostrarEven/" + idEven).then(function (response) {
    response.json().then(function (data) {
      let text = "<h2>Detalles de ";
      if (data.evento[5]) {
        text += data.evento[5];
      } else {
        text += data.evento[2];
      }
      text += "</h2><h3>Fecha</h3><p>" + data.diaEven + "</p><h3>Realizado en</h3><p>";
      if (data.evento[4]) {
        text += data.evento[4];
      } else {
        text += data.evento[3];
      }
      text += "</p><h3>Actividad realizada</h3><p>";
      if (data.evento[6]) {
        text += data.evento[6];
      } else {
        text += data.evento[5];
      }
      text += "</p><button class='btnRedondeado' onclick=location.href='/editar_evento/" + idEven
        + "' style='width: 60%; height: 2rem;'>Editar</button>";
      mostrar.innerHTML = text;
      alus = data.alus;
      mostrarAlus(0, 11, alus.length);
      caja.style.display = "flex";
    });
  });
}

function cerrarDatos() {
  footerCaja(0);
  caja.style.display = "none";
}

function footerCaja(tam) {
  let pie = document.getElementsByTagName("footer")[0];
  if (tam == 0) {
    let contenido = document.getElementById("contenido");
    if (contenido.clientHeight + pie.clientHeight >= window.screen.height) {
      pie.style.position = "relative";
      pie.style.marginTop = "10px";
    } else {
      pie.style.position = "fixed";
    }
  } else {
    if (tam + 23 >= window.screen.height) {
      pie.style.position = "inherit";
      pie.style.marginTop = ((tam + 23) - pie.clientHeight - document.getElementById("contenido").clientHeight) + "px";
    } else {

    }
  }
}