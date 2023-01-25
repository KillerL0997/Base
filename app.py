# venv/Scripts/activate
# $env:FLASK_DEBUG = "1"
# flask run

from datetime import date, datetime
from flask import Flask, jsonify, redirect, render_template, request, session, url_for, send_from_directory
from flask_migrate import Migrate
from database import db
from sqlalchemy import or_
from flask_uploads import UploadSet, IMAGES, configure_uploads
from models import horarioGim,Imagen,Notificaciones, Usuario, Gimnasio, Alumno, Eventos, Matriculas, aluEven, usuGim, usuNoti
from forms import AlumnoForm, DatoForm, ExamenForm, Gimnasio_Usuario, GimnasioForm, NotificacionForm, Usuario_Gimnasio, UsuarioForm
import random, pathlib

app= Flask(__name__)

USER_DB = "postgres"
PASS_DB = 12345
URL_DB = "localhost"
NAME_DB = "base_enat"
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = 'static/Imagenes'

db.init_app(app)

migrate = Migrate()
migrate.init_app(app, db)
app.config['SECRET_KEY'] = 'Taekwon-do_Enat'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

@app.route("/")
@app.route("/Menu")
@app.route("/Menu.html")
@app.route("/index")
@app.route("/index.html")
def base():
    fActual = datetime.now().date()
    fExamen = fechaEvento("Examen",fActual)
    fTorneo = fechaEvento("Torneo",fActual)
    fOtro = fechaEvento("Otros eventos",fActual)
    fotoExa = Imagen.query.filter(Imagen.id_evento.in_(listaEventosId("Examen"))).with_entities(Imagen.direccion).all()
    fotoTor = Imagen.query.filter(Imagen.id_evento.in_(listaEventosId("Torneo"))).with_entities(Imagen.direccion).all()
    fotoOtro = Imagen.query.filter(Imagen.id_evento.in_(listaEventosId("Otros eventos"))).with_entities(Imagen.direccion).all()
    carrExaSel = llenarCarrucelSel(fotoExa)
    carrTorSel = llenarCarrucelSel(fotoTor)
    carrOtroSel = llenarCarrucelSel(fotoOtro)
    carrExa = llenarCarrucel(fotoExa)
    carrTor = llenarCarrucel(fotoTor)
    carrOtro = llenarCarrucel(fotoOtro)
    carrFechas = preparaFechas(list((fExamen,fTorneo,fOtro)))
    return render_template("/BaseDeDatos/menu.html",
    carrFechas = carrFechas, lenCarrFechas = len(carrFechas) if carrFechas else 0, 
    carrExaSel = carrExaSel, cantCarrExaSel = len(carrExaSel),
    carrTorSel = carrTorSel, cantCarrTorSel = len(carrTorSel),
    carrOtroSel = carrOtroSel, cantCarrOtroSel = len(carrOtroSel),
    carrExa = carrExa, carrTor = carrTor, carrOtro = carrOtro)

def preparaFechas(lista):
    if not lista[0] and not lista[1] and not lista[2]:
        return None
    carr = []
    for i in range(len(lista)):
        if lista[i]:
            carr.append("carousel-item text")
            if(lista[i].tipo_de_evento != "Otros eventos"):
                carr.append("Proximo "+ lista[i].tipo_de_evento.lower() + 
                " : " + str(lista[i].fecha_evento))
            else:
                carr.append(lista[i].descripcion.capitalize() + 
                " : " + str(lista[i].fecha_evento))
    carr[0] = "carousel-item text active"
    return carr

def fechaEvento(tipo, fActual):
    return Eventos.query.filter(
        Eventos.tipo_de_evento == tipo, Eventos.fecha_evento <= fActual
        ).order_by(
            Eventos.fecha_evento
            ).with_entities(
                Eventos.fecha_evento, Eventos.descripcion, Eventos.tipo_de_evento
                ).first()

def llenarCarrucel(lista):
    if not lista:
        return ()
    carrucel = []
    for i in lista:
        carrucel.append(i[0])
    return carrucel

def llenarCarrucelSel(lista):
    if not lista:
        return ()
    carrucel = ["carousel-item active", lista[0][0]]
    for i in range(1, len(lista)):
        carrucel.append("carousel-item")
        carrucel.append(lista[i][0])
    return carrucel

def listaEventosId(tipo):
    even = Eventos.query.filter(Eventos.tipo_de_evento == tipo).order_by(Eventos.fecha_evento).with_entities(Eventos.id_evento).first()
    return even if even else ()

@app.route("/Gimnasios")
def gimnasios():
    listaGims = Gimnasio.query.all()
    listaUsu = []
    listaHorarios = []
    listaCont = []
    listaCont.append(0)
    cont = 0
    pos = 0
    hora = 0
    contHorarios = []
    contHorarios.append(0)
    for i in listaGims:
        registros = usuGim.query.filter(usuGim.id_gimnasio == i.id_gimnasio).with_entities(usuGim.id_usuario,usuGim.id_UsuGim).order_by(usuGim.id_usuario.asc()).all()
        for j in registros:
            usu = Usuario.query.filter(Usuario.id_usuario == j.id_usuario).with_entities(Usuario.nombre_usuario,Usuario.apellido_usuario).first()
            listaUsu.append(f'{usu.nombre_usuario} {usu.apellido_usuario}')
            horario = horarioGim.query.filter(horarioGim.id_UsuGim == j.id_UsuGim).with_entities(horarioGim.descripcion).first()
            if horario:
                listaHorarios.append(horario)
                hora += 1
            cont += 1
        contHorarios.append(hora)
        listaCont.append(cont)
        pos += 1
    fActual = datetime.now().date()
    fExamen = fechaEvento("Examen",fActual)
    fTorneo = fechaEvento("Torneo",fActual)
    fOtro = fechaEvento("Otros eventos",fActual)
    carrFechas = preparaFechas(list((fExamen,fTorneo,fOtro)))
    return render_template("BaseDeDatos/gimnasios.html",
    carrFechas = carrFechas, lenCarrFechas = len(carrFechas) if carrFechas else 0,
    listaGims = listaGims, listaUsu = listaUsu, listaHorarios = listaHorarios,
    listaCont = listaCont, pos = pos, contHorarios = contHorarios,
    fActual = datetime.now().date(), fExamen = fExamen[0] if fExamen else fExamen,
    fTorneo = fTorneo[0] if fTorneo else fTorneo, fOtro = fOtro[0] if fOtro else fOtro)

@app.route("/Teoria")
def teoria():
    fActual = datetime.now().date()
    fExamen = fechaEvento("Examen",fActual)
    fTorneo = fechaEvento("Torneo",fActual)
    fOtro = fechaEvento("Otros eventos",fActual)
    carrFechas = preparaFechas(list((fExamen,fTorneo,fOtro)))
    return render_template("BaseDeDatos/teoria.html",
    carrFechas = carrFechas, lenCarrFechas = len(carrFechas) if carrFechas else 0,
    fActual = datetime.now().date(), fExamen = fExamen[0] if fExamen else fExamen,
    fTorneo = fTorneo[0] if fTorneo else fTorneo, fOtro = fOtro[0] if fOtro else fOtro)

@app.route("/Base")
def inicio():
    usuarios = Usuario.query.all()
    if len(usuarios) == 0:
        return redirect(url_for('agregar_usuario', msj = "Super"))
    if "E-Mail" not in session:
        return redirect(url_for("login"))
    noti = usuNoti.query.filter(or_(usuNoti.id_Usuario == None, usuNoti.id_Usuario == session["id"])).with_entities(usuNoti.id_Notificacion)
    notificaciones = Notificaciones.query.filter(Notificaciones.id_notificacion.in_(noti)).all()
    gimnasios = False
    if session["Cargo"] == 'Administrador':
        if Gimnasio.query.limit(1):
            gimnasios = True
    else:
        if usuGim.query.filter_by(id_usuario = session["id"]).first() or usuGim.query.filter_by(id_cabeza = session["id"]).first():
            gimnasios = True
    return render_template("BaseDeDatos/Inicio_base.html", msj = session["Cargo"],
    notificaciones = notificaciones, usuario = session["id"], gimnasios = gimnasios)

@app.route("/contra/<int:id>")
def contra(id):
    obj = {}
    obj["msj"] = (Usuario.query.get(id)).contraseña_usuario
    return jsonify({'lista':obj})

@app.route("/login", methods = {"GET", "POST"})
def login():
    if request.form.getlist("reto"):
        return redirect(url_for("base"))
    if request.method == "POST":
        validar_usuario = Usuario.query.filter_by(email_usuario = request.form["E-Mail"],contraseña_usuario = request.form["password"]).first()
        if validar_usuario:
            session["E-Mail"] = validar_usuario.email_usuario
            session["Cargo"] = validar_usuario.cargo_usuario
            session["id"] = validar_usuario.id_usuario
            return redirect(url_for("inicio"))
        return render_template("BaseDeDatos/login.html", msj = "Error al ingresar los datos")
    return render_template("BaseDeDatos/login.html")

@app.route("/logout")
def logout():
    session.pop("E-Mail")
    return redirect(url_for("inicio"))

# Notificaciones
@app.route("/crear_notificacion", methods = {'GET', 'POST'})
def crear_notificacion():
    notificacion = Notificaciones()
    notiForm = NotificacionForm(obj = notificacion)
    usuarios = Gimnasio_Usuario()
    if request.method == 'POST':
        if notiForm.validate_on_submit():
            notiForm.populate_obj(notificacion)
            db.session.add(notificacion)
            db.session.commit()
            noti = usuNoti()
            noti.id_Notificacion = notificacion.id_notificacion
            if usuarios.usuario.data == "Nada":
                noti.id_Usuario = None
            else:
                noti.id_Usuario = usuarios.usuario.data
            db.session.add(noti)
            db.session.commit()
            return redirect(url_for('inicio'))
    usuario = Usuario.query.all()
    usuarios.usuario.choices.append((f'Nada',f'Todos los usuarios'))
    for i in usuario:
        usuarios.usuario.choices.append((f'{i.id_usuario}',f'{i.nombre_usuario} {i.apellido_usuario}'))
    return render_template("BaseDeDatos/crear_notificaciones.html", forma = notiForm,
    usuarios = usuarios)

@app.route("/eliminar_notificacion", methods = {'GET', 'POST'})
def eliminar_notificacion():
    notificaciones = []
    if session["Cargo"] == "Usuario":
        noti = usuNoti.query.filter_by(id_Usuario = session["id"]).all()
        for i in noti:
            notificaciones.append(Notificaciones.query.get(i.id_Notificacion))
    else:
        notificaciones = Notificaciones.query.all()
    if request.method == 'POST':
        for i in request.form.getlist("checkbox"):
            if session["Cargo"] != "Usuario":
                dato = usuNoti.query.filter_by(id_Notificacion = i).all()
                for j in dato:
                    db.session.delete(j)
                    db.session.commit()
            else:
                dato = usuNoti.query.filter_by(id_Notificacion = i, id_Usuario = session["id"]).first()
                db.session.delete(dato)
                db.session.commit()
            db.session.delete(Notificaciones.query.get(i))
            db.session.commit()
        return redirect(url_for('inicio'))
    return render_template("BaseDeDatos/eliminar_notificacion.html", notificaciones = notificaciones)

# Inicio de funciones de usuarios
@app.route("/editar_usuario/<int:id>/<string:opc>", methods = {'GET', 'POST'})
@app.route("/editar_usuario/ver_usuarios")
def editar_usuario(id, opc):
    usuario = Usuario.query.get_or_404(id)
    usuarioForma = UsuarioForm(obj = usuario)
    datoCabezas = DatoForm()
    cabezas = Usuario.query.filter_by(cabeza_de_grupo = True).all()
    for i in cabezas:
        datoCabezas.dato.choices.append((f'{i.id_usuario}',f'{i.nombre_usuario} {i.apellido_usuario}'))
    if request.method == 'POST':
        usuarioForma.populate_obj(usuario)
        cabeza = datoCabezas.dato.data
        usuario.id_cabeza = cabeza
        regis = usuGim.query.filter_by(id_usuario = id).all()
        for i in regis:
            i.id_cabeza = cabeza
            db.session.commit()
        db.session.commit()
        if session["Cargo"] == 'Usuario':
            return redirect(url_for("inicio"))
        if opc == "editar":
            return redirect(url_for("ver_usuarios", opc = "todo"))
        return redirect(url_for("inicio"))
    return render_template("BaseDeDatos/Usuarios/editar_usuario.html", forma = usuarioForma,
    cabezas = datoCabezas, msj = opc)

@app.route("/eliminar_usuario/<int:id>")
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    noti = usuNoti.query.filter_by(id_Usuario = id).all()
    for i in noti:
        db.session.delete(i)
        db.session.commit()
    registroGims = usuGim.query.filter_by(id_usuario = id).all()
    for i in registroGims:
        regisGim = usuGim.query.filter_by(id_gimnasio = i.id_gimnasio).all()
        if len(regisGim) == 1:
            (Gimnasio.query.get(regisGim[0].id_gimnasio)).habilitado = False
            db.session.commit()
        regisGim = usuGim.query.filter_by(id_usuario = id, id_gimnasio = i.id_gimnasio).first()
        temp = Alumno.query.filter_by(id_UsuGim = regisGim.id_UsuGim).all()
        for j in temp:
            j.habilitado = False
            j.fecha_Exa_Desa = datetime.utcnow()
            j.id_UsuGim = None
            db.session.commit()
        temp = horarioGim.query.filter_by(id_UsuGim = i.id_UsuGim).all()
        for j in temp:
            db.session.delete(j)
            db.session.commit()
        db.session.delete(regisGim)
        db.session.commit()
    if usuario.cabeza_de_grupo:
        alus = Usuario.query.filter_by(id_cabeza = id).all()
        for i in alus:
            i.id_cabeza = None
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for("ver_usuarios", opc = 'todo'))

@app.route("/agregar_usuario/<string:msj>", methods = {'GET','POST'})
def agregar_usuario(msj):
    usuario = Usuario()
    usuarioForm = UsuarioForm(obj = usuario)
    datoCabezas = DatoForm()
    cabezas = Usuario.query.filter_by(cabeza_de_grupo = True).all()
    for i in cabezas:
        datoCabezas.dato.choices.append((f'{i.id_usuario}',f'{i.nombre_usuario} {i.apellido_usuario}'))
    if request.method == 'POST':
        usuarioForm.populate_obj(usuario)
        usuario.apellido_usuario = usuario.apellido_usuario.capitalize()
        usuario.nombre_usuario = usuario.nombre_usuario.capitalize()
        if msj != "Super":
            text = ""
            for i in range(9):
                text += str(random.randint(0,9))
            usuario.contraseña_usuario = int(text)
        db.session.add(usuario)
        db.session.commit()
        if not usuario.cabeza_de_grupo:
            usuario.id_cabeza = datoCabezas.dato.data
        else:
            usuario.id_cabeza = usuario.id_usuario
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template("BaseDeDatos/Usuarios/agregar_usuario.html", forma = usuarioForm, cabezas = datoCabezas, msj = msj)

@app.route("/mostrar_datos_usuario/<int:id>")
def mostrar_datos_usuario(id):
    registro_gimnasios = usuGim.query.filter_by(id_usuario = id).all()
    gimnasios = []
    datoCabeza = ""
    usuarioTemp = Usuario.query.get(id)
    if usuarioTemp.cargo_usuario == "Administrador":
        datoCabeza = "Es un administrador"
    else:
        if usuarioTemp.cabeza_de_grupo == False:
            usuario = Usuario.query.get(usuarioTemp.id_cabeza)
            if usuario:
                datoCabeza = f'{usuario.nombre_usuario} {usuario.apellido_usuario}'
            else:
                datoCabeza = "Sin cabeza de grupo"
        else:
            datoCabeza = "Es cabeza de grupo"
    for i in registro_gimnasios:
        gimnasios.append(Gimnasio.query.get(i.id_gimnasio))
    return render_template("BaseDeDatos/Usuarios/mostrar_datos_usuario.html",
    usuario= Usuario.query.get_or_404(id), gimnasios = gimnasios, cabeza = datoCabeza)

@app.route("/ver_usuarios/<string:opc>")
def ver_usuarios(opc):
    usuarios = []
    if opc == 'todo':
        usuarios = Usuario.query.all()
    elif opc == 'cabeza':
        usuarios = Usuario.query.filter_by(cabeza_de_grupo = True).all()
    elif opc == 'instructor':
        usuarios = Usuario.query.filter_by(cabeza_de_grupo = False, cargo_usuario = 'Usuario').all()
    elif opc == 'usuario':
        usuarios = Usuario.query.filter_by(cargo_usuario = 'Usuario').all()
    elif opc == 'administrador':
        usuarios = Usuario.query.filter_by(cargo_usuario = 'Administrador').all()
    return render_template("BaseDeDatos/Usuarios/ver_usuarios.html", usuarios = usuarios)

@app.route("/cambiar_contraseña/<string:msj>", methods = {'GET','POST'})
def cambiar_contraseña(msj):
    if request.method == 'POST':
        contra1 = request.form.getlist("contra_1")[0]
        contra2 = request.form.getlist("contra_2")[0]
        if contra1 and contra2 and contra1 == contra2:
            usuario = Usuario.query.get(session["id"])
            if usuario.contraseña_usuario == contra1:
                return render_template("BaseDeDatos/Usuarios/cambiar_contraseña.html", msj = 'La contraseña ingresada es igual a la contraseña del usuario')
            usuario.contraseña_usuario = contra1
            db.session.commit()
            return redirect(url_for('inicio'))
        else:
            return render_template("BaseDeDatos/Usuarios/cambiar_contraseña.html", msj = 'Verifique los datos ingresados')
    return render_template("BaseDeDatos/Usuarios/cambiar_contraseña.html", msj = 'nada')

@app.route("/cabezas")
def cabezas():
    cabezas = Usuario.query.filter_by(cabeza_de_grupo = True).all()
    listaUsuarios = []
    for i in cabezas:
        usuarioObj = {}
        usuarioObj["id"] = i.id_usuario
        usuarioObj["Nombre"] = i.nombre_usuario
        usuarioObj["Apellido"] = i.apellido_usuario
        listaUsuarios.append(usuarioObj)
    return jsonify({'lista': listaUsuarios})

# Fin de funciones usuario

# Inicio de las funciones de eventos
@app.route("/editar_evento/<int:id>", methods = {'GET','POST'})
def editar_evento(id):
    evento = Eventos.query.get_or_404(id)
    eventoForma = ExamenForm(obj = evento)
    gimnasios = Usuario_Gimnasio()
    gimnasio = Gimnasio.query.all()
    for i in gimnasio:
        gimnasios.gimnasio.choices.append((f'{i.id_gimnasio}',f'{i.nombre_gimnasio} {i.direccion_gimnasio}'))
    if request.method == 'POST' and eventoForma.validate_on_submit():
        eventoForma.populate_obj(evento)
        evento.lugar_evento = (Gimnasio.query.get(gimnasios.gimnasio.data)).nombre_gimnasio
        db.session.commit()
        return redirect(url_for("ver_eventos", opc = "todo"))
    return render_template("BaseDeDatos/Eventos/editar_evento.html", forma = eventoForma, formaGim = gimnasios)

@app.route("/eliminar_evento/<int:id>")
def eliminar_evento(id):
    registros = aluEven.query.filter_by(id_evento = id).all()
    for i in registros:
        db.session.delete(i)
        db.session.commit()
    db.session.delete(Eventos.query.get(id))
    db.session.commit()
    return redirect(url_for("ver_eventos", opc = "todo"))

@app.route("/agregar_evento", methods= {'GET','POST'})
def agregar_evento():
    evento = Eventos()
    eventoForma = ExamenForm(obj = evento)
    registro_gimnasio = Usuario_Gimnasio()
    gimnasios = Gimnasio.query.all()
    for i in gimnasios:
        registro_gimnasio.gimnasio.choices.append((f'{i.id_gimnasio}',f'{i.nombre_gimnasio} {i.direccion_gimnasio}'))
    registro_gimnasio.gimnasio.choices.append(('otro','Otro lugar'))
    if request.method == 'POST' and eventoForma.validate_on_submit():
        eventoForma.populate_obj(evento)
        if registro_gimnasio.gimnasio.data == 'otro':
            evento.lugar_evento = None
        else:
            evento.lugar_evento = (Gimnasio.query.get(registro_gimnasio.gimnasio.data)).nombre_gimnasio
        db.session.add(evento)
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template("BaseDeDatos/Eventos/agregar_evento.html", forma = eventoForma,
    formaGim = registro_gimnasio)

@app.route("/mostrar_datos_evento/<int:id>")
def mostrar_datos_evento(id):
    evento = Eventos.query.get_or_404(id)
    registros = aluEven.query.filter(aluEven.id_evento == id).with_entities(aluEven.id_alumno)
    alumnos = Alumno.query.filter(Alumno.id_alumno.in_(registros)).order_by(
        Alumno.apellido_alumno.asc(), Alumno.nombre_alumno.asc()
    ).all()
    return render_template("BaseDeDatos/Eventos/mostrar_datos_evento.html", evento = evento,
    alumnos = alumnos)

@app.route("/ver_eventos/<string:opc>", methods= {'GET','POST'})
def ver_eventos(opc):
    examenes = []
    torneos = []
    otros = []
    if opc == "examen":
        examenes = Eventos.query.filter_by(tipo_de_evento = 'Examen').all()
    elif opc == "torneos":
        torneos = Eventos.query.filter_by(tipo_de_evento = 'Torneo').all()
    elif opc == "otros":
        otros = Eventos.query.filter_by(tipo_de_evento = "Otros eventos").all()
    else:
        otros = Eventos.query.filter_by(tipo_de_evento = "Otros eventos").all()
        examenes = Eventos.query.filter_by(tipo_de_evento = 'Examen').all()
        torneos = Eventos.query.filter_by(tipo_de_evento = 'Torneo').all()
    if request.method == 'POST':
        fDesde = date.min
        fHasta = date.today()
        if request.form.get('fDesde'):
            fDesde = StrADate(request.form.get('fDesde'))
        if request.form.get('fHasta'):
            fHasta = StrADate(request.form.get('fHasta'))
        if fDesde or fHasta:
            if opc == "examen":
                examenes = filtarFechasEvento(fDesde,fHasta,examenes)
            elif opc == "torneos":
                torneos = filtarFechasEvento(fDesde,fHasta,torneos)
            elif opc == "otros":
                otros = filtarFechasEvento(fDesde,fHasta,otros)
            else:
                otros = filtarFechasEvento(fDesde,fHasta,otros)
                torneos = filtarFechasEvento(fDesde,fHasta,torneos)
                examenes = filtarFechasEvento(fDesde,fHasta,examenes)
    return render_template("BaseDeDatos/Eventos/ver_eventos.html", examenes = examenes,
    torneos = torneos, otros = otros, msj = session["Cargo"], opc = opc)

def StrADate(fecha):
    return date(int(fecha[0:4]),int(fecha[5:7]),int(fecha[8:]))

def filtarFechasEvento(fDesde, fHasta, lista):
    final = []
    if fDesde and fHasta:
        for i in lista:
            if i.fecha_evento >= fDesde and i.fecha_evento <= fHasta:
                final.append(i)
    elif fDesde:
        for i in lista:
            if i.fecha_evento >= fDesde:
                final.append(i)
    else:
        for i in lista:
            if i.fecha_evento <= fHasta:
                final.append(i)
    return final

# Fin de las funciones de eventos

# Inicio de las funciones de gimnasios
@app.route("/quitar_usuarios/<int:id>", methods = {'GET','POST'})
def quitar_usuarios(id):
    gimnasio = Gimnasio.query.get(id)
    registros = []
    usuarios = []
    if session["Cargo"] == "Administrador":
        registros = usuGim.query.filter_by(id_gimnasio = id).all()
    elif (Usuario.query.get(session["id"])).cabeza_de_grupo:
        usuario = usuGim.query.filter_by(id_usuario = session["id"], id_gimnasio = id).first()
        if usuario:
            registros.append(usuario)
        usuario = Usuario.query.filter_by(id_cabeza = session["id"]).all()
        for i in usuario:
            dato = usuGim.query.filter_by(id_usuario = i.id_usuario, id_gimnasio = id).first()
            if dato and perteneceAlRegistro(dato,registros,compararUsuGim):
                registros.append(dato)
    for i in registros:
        usuarios.append(Usuario.query.get(i.id_usuario))
    if request.method == 'POST':
        seleccionados = request.form.getlist("checkbox")
        for i in seleccionados:
            regis = usuGim.query.filter_by(id_usuario = i, id_gimnasio = id).first()
            if regis:
                dato = Alumno.query.filter_by(id_UsuGim = regis.id_UsuGim).all()
                for j in dato:
                    j.habilitado = False
                    j.id_UsuGim = None
                    db.session.commit()
                db.session.delete(regis)
                db.session.commit()
        regis = usuGim.query.filter_by(id_gimnasio = id).all()
        if not regis:
            (Gimnasio.query.get(id)).habilitado = False
            db.session.commit()
        return redirect(url_for('ver_gimnasios', opc = "todo"))
    return render_template("BaseDeDatos/Gimnasios/quitar_usuarios.html",
    usuarios = usuarios, gimnasio = gimnasio)

@app.route("/agregar_usuarios/<int:id>", methods = {'GET','POST'})
def agregar_usuarios(id):
    gimnasio = Gimnasio.query.get(id)
    usuarioForm = []
    usuarios = Usuario.query.all()
    for i in usuarios:
        regis = usuGim.query.filter_by(id_usuario = i.id_usuario, id_gimnasio = id).first()
        usuario = Usuario.query.get(i.id_usuario)
        if session["Cargo"] == "Administrador":
            if not regis:
                usuarioForm.append(i)
        else:
            if not regis:
                if usuario.id_cabeza == session["id"] or usuario.id_usuario == session["id"]:
                    usuarioForm.append(i)
    if request.method == 'POST':
        seleccion = request.form.getlist("checkbox")
        if seleccion:
            for i in seleccion:
                regis = usuGim.query.filter_by(id_usuario = i, id_gimnasio = id).first()
                if not regis:
                    armarUsuGim(i,id,(Usuario.query.get(i)).id_cabeza)
        return redirect(url_for('ver_gimnasios', opc = "todo"))
    return render_template("BaseDeDatos/Gimnasios/agregar_usuarios.html", usuarioForm = usuarioForm, gimnasio = gimnasio)

@app.route("/editar_gimnasio/<int:id>", methods= {'GET','POST'})
def editar_gimnasio(id):
    msj = "Usuario"
    if session["Cargo"] == "Administrador" or (Usuario.query.get(session["id"])).cabeza_de_grupo:
        msj = "Administrador"
    gimnasio = Gimnasio.query.get_or_404(id)
    gimnasioForma = GimnasioForm(obj= gimnasio)
    if request.method == 'POST':
            gimnasioForma.populate_obj(gimnasio)
            db.session.commit()
            return redirect(url_for("ver_gimnasios", opc = "todo"))
    return render_template("BaseDeDatos/Gimnasios/editar_gimnasio.html", forma = gimnasioForma,
    msj = msj, gimnasio = id)

@app.route("/horarios/<int:id>", methods= {'GET','POST'})
def horarios(id):
    usugim = usuGim.query.filter_by(id_gimnasio = id).all()
    horarios = []
    cont = 0
    for i in usugim:
        regis = horarioGim.query.filter_by(id_UsuGim = i.id_UsuGim).all()
        usu = Usuario.query.get(i.id_usuario)
        for j in regis:
            objTemp = {}
            objTemp["id"] = j.idHorario
            objTemp["desc"] = j.descripcion
            objTemp["instructor"] = f'{usu.nombre_usuario} {usu.apellido_usuario}'
            horarios.append(objTemp)
            cont += 1
    if request.method == 'POST':
        seleccionados = request.form.getlist("checkbox")
        for i in seleccionados:
            db.session.delete(horarioGim.query.get(i))
            db.session.commit()
        horariosGim = request.form.getlist("horariosGimnasio")
        usuarios = request.form.getlist("usuarios")
        for i in range(len(horariosGim)):
            if usuarios[i] and horariosGim[i]:
                hora = horarioGim()
                hora.descripcion = horariosGim[i]
                hora.id_UsuGim = (usuGim.query.filter_by(id_gimnasio = id, id_usuario = usuarios[i]).first()).id_UsuGim
                db.session.add(hora)
                db.session.commit()
        return redirect(url_for("ver_gimnasios", opc = "todo"))
    return render_template("BaseDeDatos/Gimnasios/horarios.html", id = id,
    horarios = horarios, cont = cont)

@app.route("/agregar_gimnasio", methods = {'GET','POST'})
def agregar_gimnasio():
    gimnasio = Gimnasio()
    gimnasioForm = GimnasioForm(obj = gimnasio)
    registro_usuarios = Gimnasio_Usuario()
    usu = Usuario.query.get(session["id"])
    if session["Cargo"] == "Administrador":
        usuarios = Usuario.query.filter_by(cargo_usuario = "Usuario").all()
    elif usu.cabeza_de_grupo:
        registro_usuarios.usuario.choices.append((f'{usu.id_usuario}',f'{usu.nombre_usuario} {usu.apellido_usuario}'))
        usuarios = Usuario.query.filter_by(id_cabeza = session["id"]).all()
    if session["Cargo"] == "Administrador" or usu.cabeza_de_grupo:
        for i in usuarios:
            registro_usuarios.usuario.choices.append((f'{i.id_usuario}',f'{i.nombre_usuario} {i.apellido_usuario}'))
    else:
        registro_usuarios = []
    if request.method == 'POST' and gimnasioForm.validate_on_submit() and request.files['foto']:
        gimnasioForm.populate_obj(gimnasio)
        gimnasio.nombre_gimnasio = gimnasio.nombre_gimnasio.capitalize()
        idUsu = registro_usuarios.usuario.data
        gim = Gimnasio.query.filter_by(nombre_gimnasio = gimnasio.nombre_gimnasio, direccion_gimnasio = gimnasio.direccion_gimnasio).first()
        if gim:
            armarUsuGim(idUsu,gim.id_gimnasio,(Usuario.query.get(idUsu)).id_cabeza)
            return redirect(url_for('inicio'))
        nombre = photos.save(request.files['foto'])
        gimnasio.logo_gimnasio = "static/Imagenes/" + (url_for('obtener_nombre', filename = nombre)[9:])
        gimnasio.habilitado = True
        db.session.add(gimnasio)
        db.session.commit()
        if session["Cargo"] == "Administrador" or usu.cabeza_de_grupo:
            armarUsuGim(idUsu,gimnasio.id_gimnasio,(Usuario.query.get(idUsu)).id_cabeza)
        else:
            armarUsuGim(session["id"],gim.id_gimnasio,(usuarios.query.get(session["id"])).id_cabeza)
        return redirect(url_for('inicio'))
    return render_template("BaseDeDatos/Gimnasios/agregar_gimnasio.html",
    forma = gimnasioForm, usuarioForma = registro_usuarios)

@app.route("/mostrar_datos_gimnasio/<int:id>")
def mostrar_datos_gimnasio(id):
    gimnasio = Gimnasio.query.get_or_404(id)
    registro = usuGim.query.filter_by(id_gimnasio = id).all()
    usuarios = []
    for i in registro:
        usuarios.append(Usuario.query.get(i.id_usuario))
    alumnos = []
    if session["Cargo"] == 'Usuario':
        registro = usuGim.query.filter_by(id_usuario = session["id"], id_gimnasio = id).all()
    for i in registro:
        alus = Alumno.query.filter_by(id_UsuGim = i.id_UsuGim).all()
        alumnos += list(alus)
    return render_template("BaseDeDatos/Gimnasios/mostrar_datos_gimnasio.html", gimnasio = gimnasio, usuarios = usuarios,
    alumnos = alumnos)

@app.route("/eliminar_gimnasio/<string:numGims>/<string:corri>/<string:opc>", methods = {"GET","POST"})
def eliminar_gimnasio(numGims, corri, opc):
    if request.method != 'POST':
        listaNumsGims = []
        listaNomsGims = []
        listaNumRegis = []
        usuariosGim = []
        listaUsuarios = []
        listaNumsGims = decodificar(numGims,corri)
        for i in listaNumsGims:
            cont = 0
            regis = usuGim.query.filter_by(id_gimnasio = i).all()
            for j in regis:
                gim = Gimnasio.query.get(i)
                nom = Usuario.query.get(j.id_usuario)
                if nom and gim:
                    listaNomsGims.append(gim.nombre_gimnasio)
                    if session["Cargo"] != "Usuario" or nom.id_cabeza == session["id"] or nom.id_usuario == session["id"]:
                        cont += 1
                        listaNumRegis.append(j.id_UsuGim)
                        listaUsuarios.append(f'{nom.nombre_usuario} {nom.apellido_usuario}')
            usuariosGim.append(cont)
        return render_template("BaseDeDatos/Gimnasios/eliminar_gimnasio.html", opc = opc, listaNomsGims = listaNomsGims,
        listaUsuarios = listaUsuarios, cant = len(listaNumsGims), usuariosGim = usuariosGim, listaNumRegis = listaNumRegis)
    else:
        seleccion = request.form.getlist("seleccion")
        for i in seleccion:
            regis = usuGim.query.get(i)
            if regis:
                registros = horarioGim.query.filter_by(id_UsuGim = regis.id_UsuGim).all()
                for j in registros:
                    db.session.delete(j)
                registros = Alumno.query.filter_by(id_UsuGim = regis.id_UsuGim).all()
                for j in registros:
                    j.habilitado = False
                    j.id_UsuGim = None
                    db.session.commit()
                if len(regis.query.filter_by(id_gimnasio = regis.id_gimnasio).all()) == 1:
                    (Gimnasio.query.get(regis.id_gimnasio)).habilitado = False
                    db.session.commit()
                db.session.delete(regis)
                db.session.commit()
        return redirect(url_for("ver_gimnasios", opc = opc))

@app.route("/ver_gimnasios/<string:opc>", methods={'GET','POST'})
def ver_gimnasios(opc):
    msj = "Usuario"
    if session["Cargo"] != "Usuario" or (Usuario.query.get(session["id"])).cabeza_de_grupo:
        msj = "Administrador"
    usuarios = Gimnasio_Usuario()
    usuarios.usuario.choices.append((("Nada"),("")))
    usuario = []
    if session["Cargo"] == "Administrador":
        usuario = Usuario.query.all()
    if (Usuario.query.get(session["id"])).cabeza_de_grupo:
        usuario = Usuario.query.filter_by(id_cabeza = session["id"]).all()
    for i in usuario:
        usuarios.usuario.choices.append((f'{i.id_usuario}', f'{i.nombre_usuario} {i.apellido_usuario}'))
    gimnasios = []
    if request.method != 'POST':
        if opc == 'todo':
            registros = []
            if session["Cargo"] == 'Usuario':
                if (Usuario.query.get(session["id"])).cabeza_de_grupo:
                    registros = usuGim.query.filter_by(id_cabeza = session["id"]).all()
                else:
                    registros = usuGim.query.filter_by(id_usuario = session["id"]).all()
                for i in registros:
                    gimnasios.append(Gimnasio.query.get(i.id_gimnasio))
            else:
                gimnasios = Gimnasio.query.filter_by(habilitado = True).all()
        else:
            gimnasios = Gimnasio.query.filter_by(habilitado = False).all()
    else:
        registro = []
        if opc == 'todo':
            if usuarios.usuario.data != "Nada":
                    registro = usuGim.query.filter_by(id_usuario = usuarios.usuario.data).all()
            else:
                if session["Cargo"] != 'Administrador':
                    if (Usuario.query.get(session["id"])).cabeza_de_grupo:
                        registro = usuGim.query.filter_by(id_cabeza = session["id"]).all()
                    else:
                        registro = usuGim.query.filter_by(id_usuario = session["id"]).all()
                else:
                    gimnasios = Gimnasio.query.filter_by(habilitado = True).all()
            if registro:
                for i in registro:
                    gimnasios.append(Gimnasio.query.get(i.id_gimnasio))
        else:
            gimnasios = Gimnasio.query.filter_by(habilitado = False).all()
    return render_template("BaseDeDatos/Gimnasios/ver_gimnasios.html", gimnasios = gimnasios,
    usuarios = usuarios, msj = msj, opc = opc)

@app.route("/habiGims/<string:ids>/<string:tams>", methods = {'GET','POST'})
def habiGims(ids,tams):
    if session["Cargo"] != 'Administrador' and not Usuario.query.get(session["id"]).cabeza_de_grupo:
        for i in listaids:
            gim = Gimnasio.query.get(i)
            gim.habilitado = True
            db.session.commit()
            armarUsuGim(session["id"],i,(Usuario.query.get(session["id"])).id_cabeza)
        return
    else: 
        listaids = decodificar(ids,tams)
        listaGims = []
        listaNoms = Gimnasio_Usuario()
        listaNoms.usuario.choices.append(("Nada",""))
        usu = []
        if session["Cargo"] == 'Administrador':
            usu = Usuario.query.filter_by(cargo_usuario = "Usuario").all()
        else:
            usu = Usuario.query.filter_by(id_cabeza = session["id"]).all()
        for i in usu:
            listaNoms.usuario.choices.append((f'{i.id_usuario}',f'{i.nombre_usuario} {i.apellido_usuario}'))
        for i in listaids:
            listaGims.append((Gimnasio.query.get(i)).nombre_gimnasio)
        if request.method == 'POST':
            seleccion = request.form.getlist("checkbox")
            opc = request.form.getlist("usuario")
            for i in range(len(seleccion)):
                if opc[i] != "Nada":
                    gim = Gimnasio.query.get(seleccion[i])
                    gim.habilitado = True
                    db.session.commit()
                    armarUsuGim(opc[i],seleccion[i],(Usuario.query.get(opc[i])).id_cabeza)
            return redirect(url_for('ver_gimnasios', opc = "todo"))
        return render_template("BaseDeDatos/Gimnasios/HabilitarGims.html",
        listaids = listaids, listaNoms = listaNoms, listaGims = listaGims, cant = len(listaids))

@app.route("/elimGim/<string:ids>/<string:tams>")
def elimGim(ids,tams):
    listaIds = decodificar(ids,tams)
    for i in listaIds:
        gim = Gimnasio.query.get(i)
        url = pathlib.Path(gim.logo_gimnasio)
        url.unlink()
        horas = horarioGim.query.filter_by(id_UsuGim = i).all()
        for j in horas:
            db.session.delete(j)
            db.session.commit()
        db.session.delete(gim)
        db.session.commit()
    return redirect(url_for("ver_gimnasios", opc = "desa"))

@app.route("/desaGim/<string:ids>/<string:tams>")
def desaGim(ids,tams):
    listaIds = decodificar(ids,tams)
    for i in listaIds:
        regis = usuGim.query.filter_by(id_usuario = session["id"], id_gimnasio = i).first()
        alus = Alumno.query.filter_by(id_UsuGim = regis.id_UsuGim).all()
        for i in alus:
            i.id_UsuGim = None
            i.habilitado = False
            i.fecha_Exa_Desa = datetime.utcnow()
            db.sesion.commit()
        if len(usuGim.query.filter_by(id_gimnasio = i).all()) == 1:
            (Gimnasio.query.get(i)).habilitado = False
            db.session.delete(regis)
            db.session.commit()
    return redirect(url_for("ver_gimnasios", opc = "todo"))

@app.route("/instructores/<int:id>")
def instructores(id):
    usugim = usuGim.query.filter_by(id_gimnasio = id).all()
    listaUsu = []
    for i in usugim:
        usu = Usuario.query.get(i.id_usuario)
        objTemp = {}
        objTemp["nya"] = f'{usu.nombre_usuario} {usu.apellido_usuario}'
        objTemp["id"] = usu.id_usuario
        listaUsu.append(objTemp)
    return jsonify({'lista': listaUsu})

# Fin de las funciones de gimnasios

# Inicio de funciones de alumnos
@app.route("/mostrar_eventos/<int:id>")
def mostrar_eventos(id):
    registros = aluEven.query.filter_by(id_alumno = id).all()
    examenes = []
    torneos = []
    otros = []
    for i in registros:
        dato = Eventos.query.get(i.id_evento)
        if dato.tipo_de_evento == 'Examen':
            examenes.append(dato)
        elif dato.tipo_de_evento == 'Torneo':
            torneos.append(dato)
        else:
            otros.append(dato)
    return render_template("BaseDeDatos/Alumnos/mostrar_eventos.html", examenes = examenes,
    torneos = torneos, otros = otros, alumno = Alumno.query.get(id))

@app.route("/quitar_evento_existente/<int:id>", methods = {'GET','POST'})
def quitar_evento_existente(id):
    registros_eventos = aluEven.query.filter_by(id_alumno = id).all()
    registroEventosAlum = []
    for i in registros_eventos:
            registroEventosAlum.append(Eventos.query.get(i.id_evento))
    if request.method == 'POST':
        alum = Alumno.query.get(id)
        for i in request.form.getlist("checkbox"):
            regis = aluEven.query.filter_by(id_alumno = id, id_evento = i).first()
            if regis:
                if Eventos.query.get(i).tipo_de_evento == "Examen":
                    bajarCategoria(alum)
                db.session.delete(regis)
                db.session.commit()
        ultExa(alum)
        return redirect(url_for('ver_alumnos', opc = "todo"))
    return render_template("BaseDeDatos/Alumnos/quitar_evento_existente.html", registros = registroEventosAlum, alumno = Alumno.query.get(id))

@app.route("/agregar_evento_existente/<int:id>", methods = {'GET','POST'})
def agregar_evento_existente(id):
    registros = aluEven.query.filter(aluEven.id_alumno == id).with_entities(aluEven.id_evento)
    eventosAlu = Eventos.query.filter(Eventos.id_evento.not_in(registros)).all()
    if request.method == 'POST':
        armarAluEvens(id,request.form.getlist("checkbox"))
        return redirect(url_for('ver_alumnos', opc = "todo"))
    return render_template("BaseDeDatos/Alumnos/agregar_evento_existente.html",
    registros = eventosAlu, alumno = Alumno.query.get(id))

@app.route("/editar_alumno/<int:id>", methods = {'GET', 'POST'})
def editar_alumno(id):
    usuario_gimnasio = Usuario_Gimnasio()
    alumno = Alumno.query.get_or_404(id)
    alumnoForma = AlumnoForm(obj = alumno)
    datoCabeza = DatoForm()
    cabezas = Usuario.query.filter_by(cabeza_de_grupo = True).all()
    for i in cabezas:
        datoCabeza.dato.choices.append((f'{i.id_usuario}',f'{i.nombre_usuario} {i.apellido_usuario}'))
    cabeza = Usuario.query.get(usuGim.query.get(alumno.id_UsuGim).id_cabeza)
    # if cabeza:
    buscarYcambiar(datoCabeza.dato.choices,(f'{cabeza.id_usuario}',f'{cabeza.nombre_usuario} {cabeza.apellido_usuario}'),len(datoCabeza.dato.choices),compararData)
    regis = []
    if session["Cargo"] != 'Usuario' or (Usuario.query.get(session["id"])).cabeza_de_grupo:
        if session["Cargo"] != 'Usuario':
            regis = usuGim.query.all()
        else:
            regis = usuGim.query.filter_by(id_cabeza = session["id"]).all()
        for i in regis:
            usu = Usuario.query.get(i.id_usuario)
            usuario_gimnasio.gimnasio.choices.append((f'{i.id_UsuGim}',f'{(Gimnasio.query.get(i.id_gimnasio)).nombre_gimnasio} {usu.nombre_usuario} {usu.apellido_usuario}'))
    else:
        regis = usuGim.query.filter_by(id_usuario = session["id"]).all()
        for i in regis:
            usuario_gimnasio.gimnasio.choices.append((f'{i.id_UsuGim}',f'{(Gimnasio.query.get(i.id_gimnasio)).nombre_gimnasio}'))
    if request.method == 'POST' and alumnoForma.validate_on_submit():
        alumnoForma.populate_obj(alumno)
        alumno.id_UsuGim = usuario_gimnasio.gimnasio.data
        db.session.commit()
        return redirect(url_for('ver_alumnos', opc = 'todo'))
    registro = aluEven.query.filter_by(id_alumno = id).first()
    return render_template("BaseDeDatos/Alumnos/editar_alumno.html", forma = alumnoForma,
    gimnasios = usuario_gimnasio, registro = registro, cabezas = datoCabeza, id = id)

@app.route("/mostrar_datos_alumno/<int:id>")
def mostrar_datos_alumno(id):
    cabeza = ""
    alumno = Alumno.query.get_or_404(id)
    registro = usuGim.query.get(alumno.id_UsuGim)
    usuario = Usuario.query.get(registro.id_usuario)
    gimnasio = Gimnasio.query.get(registro.id_gimnasio)
    if usuario.cabeza_de_grupo:
        cabeza = f'{usuario.nombre_usuario} {usuario.apellido_usuario}'
    else:
        temp = Usuario.query.get(usuario.id_cabeza)
        if temp:
            cabeza = f'{temp.nombre_usuario} {temp.apellido_usuario}'
        else:
            cabeza = "sin cabeza"
    return render_template("BaseDeDatos/Alumnos/mostrar_datos_alumno.html", alumno = alumno,
    gimnasio = gimnasio, usuario = usuario, cabeza = cabeza)

@app.route("/agregar_alumno", methods = {'GET','POST'})
def agregar_alumno():
    alumno = Alumno()
    alumnoForm = AlumnoForm(obj = alumno)
    registros = []
    usuarios = Gimnasio_Usuario()
    if session["Cargo"] == 'Administrador':
        registros = usuGim.query.all()
        for i in registros:
            j = Gimnasio.query.get(i.id_gimnasio)
            k = Usuario.query.get(i.id_usuario)
            usuarios.usuario.choices.append((f'{i.id_UsuGim}',f'{j.nombre_gimnasio} {k.nombre_usuario} {k.apellido_usuario}'))
    else:
        if (Usuario.query.get(session["id"])).cabeza_de_grupo:
            registros = usuGim.query.filter_by(id_cabeza = session["id"]).all()
            for i in registros:
                j = Gimnasio.query.get(i.id_gimnasio)
                k = Usuario.query.get(i.id_usuario)
                usuarios.usuario.choices.append((f'{i.id_UsuGim}',f'{j.nombre_gimnasio} {k.nombre_usuario} {k.apellido_usuario}'))
        else:
            registros = usuGim.query.filter_by(id_usuario = session["id"]).all()
            for i in registros:
                j = Gimnasio.query.get(i.id_gimnasio)
                usuarios.usuario.choices.append((f'{j.id_gimnasio}',f'{j.nombre_gimnasio} {j.direccion_gimnasio}'))
    if request.method == 'POST':
        alumnoForm.populate_obj(alumno)
        alumno.nombre_alumno = alumno.nombre_alumno.capitalize()
        alumno.apellido_alumno = alumno.apellido_alumno.capitalize()
        alumno.nacionalidad_alumno = alumno.nacionalidad_alumno.capitalize()
        alumno.localidad_alumno = alumno.localidad_alumno.capitalize()
        if not alumno.telefono_alumno:
            alumno.telefono_alumno = 0
        alumno.id_UsuGim = usuarios.usuario.data
        alumno.habilitado = True
        db.session.add(alumno)
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template("BaseDeDatos/Alumnos/agregar_alumno.html", forma = alumnoForm, msj = session["Cargo"],
    usuarios = usuarios)

@app.route("/ver_alumnos/<string:opc>", methods={'GET','POST'})
def ver_alumnos(opc):
    alumnos = []
    msj = ""
    modo = ''
    if opc == 'todo' or opc == 'habilitado':
        modo = True
    else:
        modo = False
    form = AlumnoForm()
    opciones = Gimnasio_Usuario()
    opciones.usuario.choices = form.graduacion_alumno.choices
    gimnasios = Usuario_Gimnasio()
    gimnasios.gimnasio.choices.append(((""),("")))
    gimnasio = []
    usuario = []
    usuarios = DatoForm()
    if session["Cargo"] == 'Administrador':
        msj = "Administrador"
        regis = usuGim.query.all()
        usuarios.dato.choices.append(((""),("")))
        for i in regis:
            usu = Usuario.query.get(i.id_usuario)
            usuarios.dato.choices.append((f'{usu.id_usuario}',f'{usu.nombre_usuario} {usu.apellido_usuario}'))
        gimnasio = Gimnasio.query.filter_by(habilitado = True).all()
    elif (Usuario.query.get(session["id"])).cabeza_de_grupo:
        msj = "Administrador"
        usuario = Usuario.query.filter_by(id_cabeza = session["id"]).all()
        usuarios.dato.choices.append(((""),("")))
        for i in usuario:
            usuarios.dato.choices.append((f'{i.id_usuario}',f'{i.nombre_usuario} {i.apellido_usuario}'))
        usuario = usuGim.query.filter_by(id_cabeza = session["id"]).all()
        for i in usuario:
            if perteneceAlRegistro(i,gimnasio,compararGim):
                gimnasio.append(Gimnasio.query.get(i.id_gimnasio))
    else:
        registros = usuGim.query.filter_by(id_usuario = session["id"]).all()
        for i in registros:
            gimnasio.append(Gimnasio.query.get(i.id_gimnasio))
    for i in gimnasio:
        gimnasios.gimnasio.choices.append((f'{i.id_gimnasio}',f'{i.nombre_gimnasio}'))
    ponerPrimero(opciones.usuario.choices,len(opciones.usuario.choices), ((""),("")))
    regis = []
    if request.method != 'POST':
        if opc == 'todo' or opc == 'habilitado':
            if session["Cargo"] == 'Administrador':
                alumnos = Alumno.query.filter_by(habilitado = True).all()
            else:
                if(Usuario.query.get(session["id"])).cabeza_de_grupo:
                    regis = usuGim.query.filter_by(id_cabeza = session["id"]).all()
                else:
                    regis = usuGim.query.filter_by(id_usuario = session["id"]).all()
                for i in regis:
                    alumnos += list(Alumno.query.filter_by(id_UsuGim = i.id_UsuGim).all())
        else:
            alumnos = Alumno.query.filter_by(habilitado = False).all()
    else:
        nom = request.form.get("Nombre")
        ape = request.form.get("Apellido") 
        cate = opciones.usuario.data
        gim = gimnasios.gimnasio.data 
        fUsu = usuarios.dato.data
        alus = []
        regis = []
        if nom and ape and cate:
            alus = Alumno.query.filter(Alumno.nombre_alumno.like(f'%{nom.capitalize()}%'), Alumno.apellido_alumno.like(f'%{ape.capitalize()}%'), Alumno.graduacion_alumno.like(cate), Alumno.habilitado.is_(modo)).all()
        elif nom and not ape and not cate:
            alus = Alumno.query.filter(Alumno.nombre_alumno.like(f'%{nom.capitalize()}%'), Alumno.habilitado.is_(modo)).all()
        elif nom and ape and not cate:
            alus = Alumno.query.filter(Alumno.nombre_alumno.like(f'%{nom.capitalize()}%'), Alumno.apellido_alumno.like(f'%{ape.capitalize()}%'), Alumno.habilitado.is_(modo)).all()
        elif nom and not ape and cate:
            alus = Alumno.query.filter(Alumno.nombre_alumno.like(f'%{nom.capitalize()}%'), Alumno.graduacion_alumno.like(cate), Alumno.habilitado.is_(modo)).all()
        elif not nom and ape and cate:
            alus = Alumno.query.filter(Alumno.apellido_alumno.like(f'%{ape.capitalize()}%'), Alumno.graduacion_alumno.like(cate), Alumno.habilitado.is_(modo)).all()
        elif not nom and not ape and cate:
            alus = Alumno.query.filter(Alumno.graduacion_alumno.like(cate), Alumno.habilitado.is_(modo)).all()
        elif not nom and ape and not cate:
            alus = Alumno.query.filter(Alumno.apellido_alumno.like(f'%{ape.capitalize()}%'), Alumno.habilitado.is_(modo)).all()
        else:
            alus = Alumno.query.filter(Alumno.habilitado.is_(modo)).all()
        if modo:
            if fUsu and gim:
                regis = usuGim.query.filter_by(id_usuario = fUsu, id_gimnasio = gim).all()
            elif not fUsu and gim:
                regis = usuGim.query.filter_by(id_gimnasio = gim).all()
            elif fUsu and not gim:
                regis = usuGim.query.filter_by(id_gimnasio = gim).all()
        final = []
        if regis and alus:
            for i in regis:
                for j in alus:
                    if j.id_UsuGim == i.id_UsuGim:
                        final.append(j)
        elif alus:
            final = alus
        elif regis:
            for i in regis:
                final += list(Alumno.query.filter_by(id_UsuGim = i.id_UsuGim, habilitado = modo).all())
        alumnos = final
    return render_template("BaseDeDatos/Alumnos/ver_alumnos.html", alumnos = alumnos, gimnasios = gimnasios,
    usuarios = usuarios, msj = msj, modo = modo, opc = opc, opciones = opciones)

@app.route("/habiAlums/<string:ids>/<string:tams>", methods = {'GET','POST'})
def habiAlums(ids,tams):
    listaids = decodificar(ids,tams)
    if(request.method == 'POST'):
        usu = request.form.getlist("usuario")
        gim = request.form.getlist("gimnasio")
        for i in range(len(listaids)):
            if(usu[i]!= "Nada" and gim[i] != "Nada"):
                regi = usuGim.query.filter_by(id_usuario = usu[i], id_gimnasio = gim[i]).first()
                alum = Alumno.query.get(listaids[i])
                alum.habilitado = True
                alum.id_UsuGim = regi.id_UsuGim
                ultExa(alum)
                db.session.commit()
        return redirect(url_for("ver_alumnos", opc = "todo"))
    listaAlums = []
    listaGims = []
    msj = True
    if session["Cargo"] == "Usuario" and not (Usuario.query.get(session["id"])).cabeza_de_grupo:
        msj = False
    gimnasio = Usuario_Gimnasio()
    gimnasio.gimnasio.choices.append((f'Nada',f''))
    usuario = Gimnasio_Usuario()
    usuario.usuario.choices.append((f'Nada',f''))
    if session["Cargo"] == "Usuario" and not (Usuario.query.get(session["id"])).cabeza_de_grupo:
        regis = usuGim.query.filter_by(id_usuario = session["id"]).all()
        for i in regis:
            gimnasio.gimnasio.choices.append((f'{i.id_UsuGim}',f'{(Gimnasio.query.get(i.id_gimnasio)).nombre_gimnasio}'))
    else:
        if session["Cargo"] != "Usuario":
            regis = usuGim.query.all()
        else:
            regis = usuGim.query.filter_by(id_cabeza = session["id"]).all()
        final = []
        for i in regis:
            gim = Gimnasio.query.get(i.id_gimnasio)
            if perteneceAlRegistro(gim,final,compararGim):
                gimnasio.gimnasio.choices.append((f'{gim.id_gimnasio}',f'{gim.nombre_gimnasio}'))
                final.append(gim)
        for i in range(len(listaids)):
            listaGims.append(gimnasio)
    for i in listaids:
        alum = Alumno.query.get(i)
        listaAlums.append(alum)
    return render_template("BaseDeDatos/Alumnos/habilitarAlus.html",
    listaAlus = listaAlums, listaAlusNums = listaids, cant = len(listaids),
    listaGims = listaGims, usuarios = usuario, msj = msj)

@app.route("/elimAlus/<string:ids>/<string:tams>")
def elimAlus(ids,tams):
    listaAlus = decodificar(ids,tams)
    for i in listaAlus:
        regis = aluEven.query.filter_by(id_alumno = i).all()
        for j in regis:
            db.session.delete(j)
            db.session.commit()
        regis = Matriculas.query.filter_by(id_Alumno = i).all()
        for j in regis:
            db.session.delete(j)
            db.session.commit()
        db.session.delete(Alumno.query.get(i))
        db.session.commit()
    return redirect(url_for("ver_alumnos", opc = "deshabilitado"))

@app.route("/desaAlum/<string:ids>/<string:tams>")
def desaAlum(ids,tams):
    listaIds = decodificar(ids,tams)
    for i in listaIds:
        alum = Alumno.query.get(i)
        alum.habilitado = False
        alum.fecha_Exa_Desa = datetime.utcnow()
        alum.id_UsuGim = None
        db.session.commit()
    return redirect(url_for("ver_alumnos", opc = "deshabilitado"))

@app.route("/sumarAevento/<string:ids>/<string:tams>/<string:evento>")
def sumarAevento(ids,tams,evento):
    listaIds = decodificar(ids,tams)
    eventoReci = eventoReciente(evento)
    llenarEvento(listaIds,eventoReci,evento)
    return redirect(url_for("ver_alumnos", opc = "habilitado"))

@app.route("/cambioUsuario/<lugar>")
def cambioUsuario(lugar):
    listaUsuarios = []
    regis = {}
    if lugar != "Nada":
        regis = usuGim.query.filter_by(id_gimnasio = lugar).all()
    else:
        regis = usuGim.query.all()
    for i in regis:
        dato = Usuario.query.get(i.id_usuario)
        if dato and perteneceAlRegistro(dato,listaUsuarios,compararUsu):
            usuarioObj = {} 
            # id_usuario
            usuarioObj["id"] = dato.id_usuario
            usuarioObj["Nombre"] = dato.nombre_usuario
            usuarioObj["Apellido"] = dato.apellido_usuario
            listaUsuarios.append(usuarioObj)
    return jsonify({'lista': listaUsuarios})

@app.route("/buscarAlumno", methods={'GET','POST'})
def buscarAlumno():
    alumnosHabi = []
    alumnosDesa = []
    if request.method == 'POST':
        nom = request.form.get("nombre")
        ape = request.form.get("apellido")
        if nom and ape:
            alum = Alumno.query.filter(Alumno.nombre_alumno.like(f'%{nom.capitalize()}%'),Alumno.apellido_alumno.like(f'%{ape.capitalize()}%')).all()
        elif not nom and ape:
            alum = Alumno.query.filter(Alumno.apellido_alumno.like(f'%{ape.capitalize()}%')).all()
        elif nom and not ape:
            alum = Alumno.query.filter(Alumno.nombre_alumno.like(f'%{nom.capitalize()}%')).all()
        else:
            alum = []
        for i in alum:
            objTemp = {}
            objTemp["nombre"] = i.nombre_alumno
            objTemp["apellido"] = i.apellido_alumno
            objTemp["categoria"] = f'{i.graduacion_alumno}'
            if i.habilitado:
                usugim = usuGim.query.get(i.id_UsuGim)
                objTemp["gimnasio"] = (Gimnasio.query.get(usugim.id_gimnasio)).nombre_gimnasio
                usu = Usuario.query.get(usugim.id_usuario)
                objTemp["instructor"] = f'{usu.nombre_usuario} {usu.apellido_usuario}'
                alumnosHabi.append(objTemp)
            else:
                objTemp["fecha"] = i.fecha_Exa_Desa
                objTemp["localidad"] = f'{i.localidad_alumno}'
                alumnosDesa.append(objTemp)
    return render_template("BaseDeDatos/Alumnos/buscarAlumno.html",
    alumnosHabi = alumnosHabi, alumnosDesa = alumnosDesa)

# Fin de funciones de alumnos

# Matriculas
@app.route("/ver_matriculas/<string:opc>", methods = {'GET','POST'})
def ver_matriculas(opc):
    usuarios = DatoForm()
    usuarios.dato.choices.append(('Nada',''))
    for i in (Usuario.query.all()):
        if usuGim.query.filter_by(id_usuario = i.id_usuario).first():
            usuarios.dato.choices.append((f'{i.id_usuario}',f'{i.nombre_usuario} {i.apellido_usuario}'))
    alumnos = Alumno.query.filter_by(habilitado = True).all()
    if request.method == 'POST':
        alumnos = []
        registros = []
        # 1º usuario , 2º nombre
        if usuarios.dato.data != 'Nada':
            registros = usuGim.query.filter_by(id_usuario = usuarios.dato.data).all()
        nom = request.form.get("Nombre")
        ape = request.form.get("Apellido")
        alus = []
        if nom or ape:
            if nom and ape:
                alus = Alumno.query.filter(Alumno.nombre_alumno.like(f'%{nom.capitalize()}%'), Alumno.apellido_alumno.like(f'%{ape.capitalize()}%')).all()
            elif nom:
                alus = Alumno.query.filter(Alumno.nombre_alumno.like(f'%{nom.capitalize()}%')).all()
            elif ape:
                alus = Alumno.query.filter(Alumno.apellido_alumno.like(f'%{ape.capitalize()}%')).all()
        if registros and alus:
            final = []
            for i in registros:
                for j in alus:
                    if j.id_UsuGim == i.id_UsuGim:
                        final.append(j)
            alumnos = final
        elif alus:
            alumnos = alus
        elif registros:
            for i in registros:
                alumnos += list(Alumno.query.filter_by(id_UsuGim = i.id_UsuGim).all())
        else:
            alumnos = Alumno.query.filter_by(habilitado = True).all()
    return render_template("BaseDeDatos/Matriculas/ver_matriculas.html", usuarios = usuarios,
    alumnos = alumnos, opc = opc)

@app.route("/crear/<string:opc>/<string:ids>/<string:tams>")
def crear(opc,ids,tams):
    listaIds = decodificar(ids,tams)
    fecha = date.today()
    for i in listaIds:
        alum = Alumno.query.get(i)
        if alum:
            if opc == "AATEE" and (alum.fecha_Aatee != fecha or alum.fecha_Aatee == None):
                armarMatricula(fecha,opc,i)
                alum.fecha_Aatee = fecha
            if opc == "FETRA" and (alum.fecha_Fetra != fecha or alum.fecha_Fetra == None):
                armarMatricula(fecha,opc,i)
                alum.fecha_Fetra = fecha
            if opc == "ENAT" and (alum.fecha_Enat != fecha or alum.fecha_Enat == None):
                armarMatricula(fecha,opc,i)
                alum.fecha_Enat = fecha
            db.session.commit()
    return redirect(url_for("ver_matriculas", opc = "todo"))

def armarMatricula(fecha,tipo,id):
    matri = Matriculas()
    matri.tipo = tipo
    matri.id_Alumno = id
    matri.fecha = fecha
    db.session.add(matri)
    db.session.commit()

@app.route("/Detalles_matriculas/<int:id>")
def Detalles_matriculas(id):
    return render_template("/BaseDeDatos/Matriculas/Detalles_matriculas.html",
    matri_AATEE = Matriculas.query.filter_by(tipo = "AATEE", id_Alumno = id).all(),
    matri_ENAT = Matriculas.query.filter_by(tipo = "ENAT", id_Alumno = id).all(),
    matri_FETRA = Matriculas.query.filter_by(tipo = "FETRA", id_Alumno = id).all())

@app.route("/Editar_matriculas/<int:id>/<string:modo>", methods = {'GET','POST'})
def Editar_matriculas(id,modo):
    matri_AATEE = Matriculas.query.filter_by(tipo = "AATEE", id_Alumno = id).all()
    matri_ENAT = Matriculas.query.filter_by(tipo = "ENAT", id_Alumno = id).all()
    matri_FETRA = Matriculas.query.filter_by(tipo = "FETRA", id_Alumno = id).all()
    listaChecks = preparaMatris(matri_AATEE) + preparaMatris(matri_ENAT) + preparaMatris(matri_FETRA)
    if request.method == 'POST':
        if modo == 'editar':
            # por cada checkbox va una fecha
            fechas = request.form.getlist("fecha_AATEE")
            seleccion = request.form.getlist("checkbox_AATEE")
            if seleccion and fechas and fechas[0]:
                (Alumno.query.get(id)).fecha_Aatee = fechaMatri(fechas,seleccion,id,"AATEE")
                db.session.commit()

            fechas = request.form.getlist("fecha_ENAT")
            seleccion = request.form.getlist("checkbox_ENAT")
            if seleccion and fechas and fechas[0]:
                (Alumno.query.get(id)).fecha_Enat = fechaMatri(fechas,seleccion,id,"ENAT")
                db.session.commit()

            fechas = request.form.getlist("fecha_FETRA")
            seleccion = request.form.getlist("checkbox_FETRA")
            if seleccion and fechas and fechas[0]:
                (Alumno.query.get(id)).fecha_Fetra = fechaMatri(fechas,seleccion,id,"FETRA")
                db.session.commit()
        else:
            seleccion = request.form.getlist("checkbox_FETRA")
            if seleccion:
                borrarMatricula(seleccion)
                (Alumno.query.get(id)).fecha_Fetra = ultMatri(id,"FETRA")
                db.session.commit()
            seleccion = request.form.getlist("checkbox_ENAT")
            if seleccion:
                borrarMatricula(seleccion)
                (Alumno.query.get(id)).fecha_Enat = ultMatri(id,"ENAT")
                db.session.commit()
            seleccion = request.form.getlist("checkbox_AATEE")
            if seleccion:
                borrarMatricula(seleccion)
                (Alumno.query.get(id)).fecha_Aatee = ultMatri(id,"AATEE")
                db.session.commit()
        return redirect(url_for("ver_matriculas", opc = "todo"))
    return render_template("/BaseDeDatos/Matriculas/Editar_matriculas.html",
    matri_AATEE = matri_AATEE, matri_ENAT = matri_ENAT, matri_FETRA = matri_FETRA,
    id = id, modo = modo, idmatris = listaChecks, tamAatee = len(matri_AATEE),
    tamEnat = len(matri_ENAT), tamFetra = len(matri_FETRA))

@app.route("/agregarMatriculas/<int:id>", methods = {'GET','POST'})
def agregarMatriculas(id):
    if request.method == 'POST':
        matriAATEE = request.form.getlist("MatriAATEE")
        matriEnat = request.form.getlist("MatriENAT")
        matriFetra = request.form.getlist("MatriFetra")
        for i in matriAATEE:
            armarMatricula(i,'AATEE',id)
        for i in matriEnat:
            armarMatricula(i,'ENAT',id)
        for i in matriFetra:
            armarMatricula(i,'FETRA',id)
        return redirect(url_for("ver_matriculas", opc = 'todo'))
    return render_template("/BaseDeDatos/Matriculas/AgregarMatriculas.html", id = id)

# Imagenes
@app.route("/ver_imagenes/<string:opc>", methods = {'GET','POST'})
def ver_imagenes(opc):
    if request.method == 'POST':
        seleccionados = request.form.getlist("checkboxImagen")
        for i in seleccionados:
            dato = Imagen.query.get(i)
            url = pathlib.Path("static/" + dato.direccion)
            url.unlink()
            db.session.delete(dato)
            db.session.commit()
    fotoExa = []
    fotoTor = []
    fotoAct = []
    if opc == "todo":
        fotoExa = Imagen.query.filter_by(tipo_imagen = "Examen").all()
        fotoTor = Imagen.query.filter_by(tipo_imagen = "Torneo").all()
        fotoAct = Imagen.query.filter_by(tipo_imagen = "Otros eventos").all()
    elif opc == "Examen":
        fotoExa = Imagen.query.filter_by(tipo_imagen = "Examen").all()
    elif opc == "Torneo":
        fotoTor = Imagen.query.filter_by(tipo_imagen = "Torneo").all()
    elif opc == "Otros_eventos":
        fotoAct = Imagen.query.filter_by(tipo_imagen = "Otros eventos").all()
    return render_template("/BaseDeDatos/Imagenes/MostrarImagenes.html",
    fotoExa = fotoExa, fotoTor = fotoTor, fotoAct= fotoAct)

@app.route("/subir_imagenes/<string:tipo>", methods = {'GET','POST'})
def subir_imagenes(tipo):
    if request.method == 'POST' and request.files:
        if tipo == "Examen" or tipo == "Torneo" or tipo == "Otros_eventos":
            if tipo == "Otros_eventos":
                tipo = "Otros eventos"
            fotos = Imagen.query.filter_by(tipo_imagen = tipo).all()
            for i in fotos:
                url = pathlib.Path("static/" + i.direccion)
                url.unlink()
                db.session.delete(i)
                db.session.commit()
        if tipo == "Aexamen" or tipo == "Atorneo" or tipo == "AOtros_eventos":
            tipo = tipo[1:]
            tipo = tipo.capitalize()
        if tipo == "Otros_eventos":
            tipo = "Otros eventos"
        if Eventos.query.filter_by(tipo_de_evento = tipo).first():
            if tipo == "Otros eventos":
                tipo = "Otros_eventos"
            ultEvento = []
            if tipo == "Examen":
                ultEvento = Eventos.query.filter_by(tipo_de_evento = "Examen").all()
            elif tipo == "Torneo":
                ultEvento = Eventos.query.filter_by(tipo_de_evento = "Torneo").all()
            else:
                ultEvento = Eventos.query.filter_by(tipo_de_evento = "Otros eventos").all()
            evento = ultimoEvento(ultEvento)
            for i in request.files.getlist("foto"):
                imagen = Imagen()
                nombre = photos.save(i,tipo)
                imagen.direccion = "Imagenes" + url_for('obtener_nombre', filename = nombre)[8:]
                if tipo == "Examen" or tipo == "Torneo":
                    imagen.tipo_imagen = tipo
                else:
                    imagen.tipo_imagen = "Otros eventos"
                imagen.id_evento = evento
                db.session.add(imagen)
                db.session.commit()
        return redirect(url_for("ver_imagenes", opc = "todo"))
    return render_template("/BaseDeDatos/Imagenes/SubirImagenes.html")

@app.route("/uploads/<filename>")
def obtener_nombre(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)

def armarUsuGim(usu,gim,cabeza):
    regis = usuGim()
    regis.id_usuario = usu
    regis.id_gimnasio = gim
    regis.id_cabeza = cabeza
    db.session.add(regis)
    db.session.commit()

def armarAluEvens(alu,evens):
    alum = Alumno.query.get(alu)
    for i in evens:
        regis = aluEven()
        regis.id_alumno = alu
        regis.id_evento = i
        db.session.add(regis)
        db.session.commit()
        if (Eventos.query.get(i)).tipo_de_evento == "Examen":
            subirCategoria(alum)
    if Eventos.query.filter(Eventos.id_evento.in_(aluEven.query.filter(aluEven.id_alumno == alu).with_entities(aluEven.id_evento)), Eventos.tipo_de_evento == "Examen").first():
        alum.fecha_Exa_Desa = ultExa(alum)

def perteneceAlRegistro(dato, lista, comparar):
    for i in lista:
        if comparar(dato,i):
            return False
    return True

def compararUsuGim(dato1, dato2):
    return (dato1.id_usuario == dato2.id_usuario and dato1.id_gimnasio == dato2.id_gimnasio)

def compararGim(dato1,dato2):
    return dato1.id_gimnasio == dato2.id_gimnasio

def compararUsu(dato1,dato2):
    return dato1.id_usuario == dato2["id"]

def compararIdEven(dato1,dato2):
    return dato1.id_evento == dato2.id_evento

def compararIdAlus(dato1,dato2):
    return dato1.id_alumno == dato2.id_alumno

def ultExa(alum):
    regis = aluEven.query.filter(aluEven.id_alumno == alum.id_alumno).with_entities(aluEven.id_evento)
    evento = Eventos.query.filter(Eventos.id_evento.in_(regis)).order_by(Eventos.fecha_evento.desc()).first()
    if evento:
        alum.fecha_Exa_Desa = evento.fecha_evento
    else:
        alum.fecha_Exa_Desa = None
    db.session.commit()

def ponerPrimero(lista, tamLista, val):
    lista.append(val)
    for i in range(tamLista):
        nue = lista[tamLista]
        lista[tamLista] = lista[i]
        lista[i] = nue

def preparaMatris(matris):
    filtro = []
    tam = len(matris)
    if tam == 0:
        return []
    check = f'{corrimiento(1)}{0}{corrimiento(matris[0].id_matricula)}{matris[0].id_matricula}'
    filtro.append(check)
    if tam - 1 > 0:
        for i in range(tam - 1):
            check = f'{corrimiento(i)}{i}{corrimiento(matris[i].id_matricula)}{matris[i].id_matricula}'
            filtro.append(check)
    return filtro

def corrimiento(num):
    i = 0
    div = 1
    while int(num / div) > 0:
        div *= 10
        i += 1
    return i

def borrarMatricula(seleccion):
    for i in seleccion:
        matri = Matriculas.query.get(i)
        if matri:
            db.session.delete(matri)
            db.session.commit()

def ultMatri(id, tipoMatri):
    matriAlum = Matriculas.query.filter_by(tipo = tipoMatri, id_Alumno = id).all()
    if not matriAlum:
        return None
    else:
        fecha = matriAlum[0].fecha
        for i in matriAlum:
            if fecha < i.fecha:
                fecha = i.fecha
        return fecha

def fechaMatri(fechas,seleccion,id,tipo):
    tam = len(fechas)
    for i in seleccion:
        cant = int(seleccion[0])
        num = int(seleccion[1])
        if cant - 1 > 0:
            for j in range(cant - 1):
                num = (num * 10) + seleccion[j + 2]
        if tam > num and fechas[num]:
            pos = seleccion[1 + cant] 
            sel = seleccion[pos]
            if pos - 1 > 0:
                for j in range(pos - 1):
                    sel = (sel * 10) + seleccion[pos + j + 1]
            (Matriculas.query.get(sel)).fecha = fechas[num]
    return ultMatri(id,tipo)

def ultimoEvento(eventos):
    fecha = date.min
    id = 0
    for i in eventos:
        if fecha < i.fecha_evento:
            id = i.id_evento
    return id

def subirCategoria(dato):
    if dato.graduacion_alumno == "Blanco":
        dato.graduacion_alumno = "Blanco Pta. Amarilla"
    elif dato.graduacion_alumno == "Blanco Pta. Amarilla":
        dato.graduacion_alumno = "Amarillo"
    elif dato.graduacion_alumno == "Amarillo":
        dato.graduacion_alumno = "Amarillo Pta. Verde"
    elif dato.graduacion_alumno == "Amarillo Pta. Verde":
        dato.graduacion_alumno = "Verde"
    elif dato.graduacion_alumno == "Verde":
        dato.graduacion_alumno = "Verde Pta. Azul"
    elif dato.graduacion_alumno == "Verde Pta. Azul":
        dato.graduacion_alumno = "Azul"
    elif dato.graduacion_alumno == "Azul":
        dato.graduacion_alumno = "Azul Pta. Roja"
    elif dato.graduacion_alumno == "Azul Pta. Roja":
        dato.graduacion_alumno = "Rojo"
    elif dato.graduacion_alumno == "Rojo":
        dato.graduacion_alumno = "Rojo Pta. Negra"
    elif dato.graduacion_alumno == "Rojo Pta. Negra":
        dato.graduacion_alumno = "I Dan"
    elif dato.graduacion_alumno == "I Dan":
        dato.graduacion_alumno = "II Dan"
    elif dato.graduacion_alumno == "II Dan":
        dato.graduacion_alumno = "III Dan"
    elif dato.graduacion_alumno == "III Dan":
        dato.graduacion_alumno = "IV Dan"
    elif dato.graduacion_alumno == "IV Dan":
        dato.graduacion_alumno = "V Dan"
    elif dato.graduacion_alumno == "V Dan":
        dato.graduacion_alumno = "VI Dan"
    elif dato.graduacion_alumno == "VI Dan":
        dato.graduacion_alumno = "VII Dan"
    db.session.commit()

def bajarCategoria(dato):
    if dato.graduacion_alumno == "VII Dan":
        dato.graduacion_alumno = "VI Dan"
    elif dato.graduacion_alumno == "VI Dan":
        dato.graduacion_alumno = "V Dan"
    elif dato.graduacion_alumno == "V Dan":
        dato.graduacion_alumno = "IV Dan"
    elif dato.graduacion_alumno == "IV Dan":
        dato.graduacion_alumno = "III Dan"
    elif dato.graduacion_alumno == "III Dan":
        dato.graduacion_alumno = "II Dan"
    elif dato.graduacion_alumno == "II Dan":
        dato.graduacion_alumno = "I Dan"
    elif dato.graduacion_alumno == "I Dan":
        dato.graduacion_alumno = "Rojo Pta. Negra"
    elif dato.graduacion_alumno == "Rojo Pta. Negra":
        dato.graduacion_alumno = "Rojo"
    elif dato.graduacion_alumno == "Rojo":
        dato.graduacion_alumno = "Azul Pta. Roja"
    elif dato.graduacion_alumno == "Azul Pta. Roja":
        dato.graduacion_alumno = "Azul"
    elif dato.graduacion_alumno == "Azul":
        dato.graduacion_alumno = "Verde Pta. Azul"
    elif dato.graduacion_alumno == "Verde Pta. Azul":
        dato.graduacion_alumno = "Verde"
    elif dato.graduacion_alumno == "Verde":
        dato.graduacion_alumno = "Amarillo Pta. Verde"
    elif dato.graduacion_alumno == "Amarillo Pta. Verde":
        dato.graduacion_alumno = "Amarillo"
    elif dato.graduacion_alumno == "Amarillo":
        dato.graduacion_alumno = "Blanco Pta. Amarilla"
    elif dato.graduacion_alumno == "Blanco Pta. Amarilla":
        dato.graduacion_alumno = "Blanco"
    db.session.commit()

def eventoReciente(opc):
    lista = Eventos.query.filter_by(tipo_de_evento = opc).all()
    dato = []
    for i in lista:
        if not dato or dato.fecha_evento < i.fecha_evento:
            dato = i
    return dato

def buscarYcambiar(lista, datoBus, tamLista, comparar):
    dato = []
    i = 0
    for i in range(tamLista):
        if comparar(datoBus,lista[i]):
            break
    dato = lista[i]
    lista[i] = lista[0]
    lista[0] = dato

def compararData(dato1,dato2):
    return dato1 == dato2

def llenarEvento(seleccionados, evento, opc):
    for i in seleccionados:
        dato = Alumno.query.get(i)
        if dato.fecha_Exa_Desa == None or dato.fecha_Exa_Desa != evento.fecha_evento:
            regis = aluEven()
            regis.id_alumno = i
            regis.id_evento = evento.id_evento
            db.session.add(regis)
            db.session.commit()
            if opc == "Examen":
                subirCategoria(dato)
                ultExa(dato)
            db.session.commit()

def decodificar(ids,tams):
    listaIds = []
    lim = len(tams)
    cont = 0
    for i in range(lim):
        num = 0
        j = 0
        for j in range(int(tams[i])):
            num = (num * 10) + (int(ids[cont + j]))
        cont += (j + 1)
        listaIds.append(num)
    return listaIds