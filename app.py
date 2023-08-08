# venv/Scripts/activate
# $env:FLASK_DEBUG = "1"
# flask run

# Limpiar codigo y plantillas
# Cambiar la tabla alumno para que no almacene el ultimo examen ni la ultima matricula
# Eliminar los "POST" de los "Ver"

from datetime import date, datetime, timedelta
from flask import Flask, jsonify, redirect, render_template, request, session, url_for, send_from_directory
from flask_migrate import Migrate
from database import db
from sqlalchemy import or_, insert, update, delete, select, create_engine, func
from flask_uploads import UploadSet, IMAGES, configure_uploads
from models import horarioGim, Imagen, Notificaciones, Usuario, Gimnasio, Alumno, Eventos, Matriculas, aluEven, usuGim, usuNoti
from forms import AlumnoForm, DatoForm, ExamenForm, Gimnasio_Usuario, GimnasioForm, NotificacionForm, Usuario_Gimnasio, UsuarioForm
import pathlib
import os
import shutil
import flask

app = Flask(__name__)

USER_DB = "postgres"
PASS_DB = 12345
URL_DB = "localhost"
NAME_DB = "base_enat"
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(
    app.root_path, 'static/Imagenes')
app.config['UPLOADED_PHOTOS_ALLOW'] = set(
    ['png', 'jpg', 'jpeg', 'jfif', 'jpeg'])

db.init_app(app)

migrate = Migrate()
migrate.init_app(app, db)
app.config['SECRET_KEY'] = 'Taekwon-do_Enat'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

motor = create_engine(FULL_URL_DB, echo=True, pool_timeout=0.5, pool_recycle=299,
                      pool_size=20, pool_pre_ping= True)


ESPERA = 1
CATEGORIAS = ['Blanco', 'Blanco Pta. Amarilla', 'Amarillo', 'Amarillo Pta. Verde', 'Verde',
              'Verde Pta. Azul', 'Azul', 'Azul Pta. Roja', 'Rojo', 'Rojo Pta. Negra', 'I Dan',
              'II Dan', 'III Dan', 'IV Dan', 'V Dan', 'VI Dan', 'VII Dan']


@app.route("/")
@app.route("/Menu")
@app.route("/Menu.html")
@app.route("/index")
@app.route("/index.html")
def base():
    fExamen = fechaEventoProx("Examen")
    fTorneo = fechaEventoProx("Torneo")
    fOtro = fechaEventoProx("Otros eventos")
    fotoExa = Imagen.query.filter(Imagen.id_evento.in_(
        listaEventosId("Examen"))).with_entities(Imagen.direccion).all()
    fotoTor = Imagen.query.filter(Imagen.id_evento.in_(
        listaEventosId("Torneo"))).with_entities(Imagen.direccion).all()
    fotoOtro = Imagen.query.filter(Imagen.id_evento.in_(
        listaEventosId("Otros eventos"))).with_entities(Imagen.direccion).all()
    carrExaSel = llenarCarrucelSel(fotoExa)
    carrTorSel = llenarCarrucelSel(fotoTor)
    carrOtroSel = llenarCarrucelSel(fotoOtro)
    carrExa = llenarCarrucel(fotoExa)
    carrTor = llenarCarrucel(fotoTor)
    carrOtro = llenarCarrucel(fotoOtro)
    carrFechas = preparaFechas(list((fExamen, fTorneo, fOtro)))
    fExamen = fechaEvento("Examen")
    fTorneo = fechaEvento("Torneo")
    fOtro = fechaEvento("Otros eventos")
    return render_template("/BaseDeDatos/menu.html", carrFechas=carrFechas,
                           carrExaSel=carrExaSel, carrTorSel=carrTorSel,
                           carrOtroSel=carrOtroSel, carrExa=carrExa, carrTor=carrTor,
                           carrOtro=carrOtro, fExamen=fExamen, fTorneo=fTorneo, fOtro=fOtro)


def preparaFechas(lista):
    if not lista[0] and not lista[1] and not lista[2]:
        return None
    carr = []
    for elem in lista:
        if elem:
            fecha = []
            fecha.append("carousel-item text")
            if (elem.tipo_de_evento != "Otros eventos"):
                fecha.append(
                    f'Proximo {elem.tipo_de_evento.lower()} : {elem.fecha_evento.day}/{elem.fecha_evento.month}/{elem.fecha_evento.year}')
            else:
                fecha.append(
                    f'{elem.tipoOpc.capitalize()} : {elem.fecha_evento.day}/{elem.fecha_evento.month}/{elem.fecha_evento.year}')
            carr.append(fecha)
    carr[0][0] = "carousel-item text active"
    return carr


def fechaEvento(tipo):
    return Eventos.query.filter(
        Eventos.tipo_de_evento == tipo, Eventos.fecha_evento < datetime.now().date()
    ).order_by(
        Eventos.fecha_evento.desc()
    ).with_entities(
        Eventos.fecha_evento, Eventos.lugarOpc, Eventos.tipo_de_evento, Eventos.tipoOpc,
        Eventos.actRealizada
    ).first()


def fechaEventoProx(tipo):
    return Eventos.query.filter(
        Eventos.tipo_de_evento == tipo, Eventos.fecha_evento >= datetime.now().date()
    ).order_by(
        Eventos.fecha_evento.asc()
    ).with_entities(
        Eventos.fecha_evento, Eventos.lugarOpc, Eventos.tipo_de_evento, Eventos.tipoOpc
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
    carrucel = []
    for i in lista:
        carrucel.append(["carousel-item", i.direccion])
    carrucel[0][0] = "carousel-item active"
    return carrucel


def listaEventosId(tipo):
    even = Eventos.query.filter(
        Eventos.tipo_de_evento == tipo, Eventos.fecha_evento < datetime.now().date()
        ).order_by(Eventos.fecha_evento.desc()).with_entities(Eventos.id_evento).first()
    return even if even else ()


@app.route("/Gimnasios")
def gimnasios():
    lista = Gimnasio.query.filter(
        Gimnasio.habilitado == True
    ).all()
    listaGims = []
    for i in lista:
        gimnasio = Gimnasio.query.get(i.id_gimnasio)
        mostrarGim = [
            gimnasio.nombre_gimnasio, gimnasio.logo_gimnasio, gimnasio.direccion_gimnasio,
            gimnasio.instagram_gimnasio, gimnasio.whats_gimnasio, gimnasio.ubicacion_gimnasio,
            gimnasio.face_gimnasio
        ]
        usugim = usuGim.query.filter(
            usuGim.id_gimnasio == i.id_gimnasio
        ).all()
        usuarios = []
        horas = []
        for j in usugim:
            usu = Usuario.query.get(j.id_usuario)
            usuarios.append(f'{usu.apellido_usuario} {usu.nombre_usuario}')
        mostrarGim.append(usuarios)
        for j in usugim:
            hora = horarioGim.query.filter(
                horarioGim.id_UsuGim == j.id_UsuGim).all()
            if hora:
                for h in hora:
                    horas.append(h.descripcion)
        mostrarGim.append(horas)
        listaGims.append(mostrarGim)
    fExamen = fechaEventoProx("Examen")
    fTorneo = fechaEventoProx("Torneo")
    fOtro = fechaEventoProx("Otros eventos")
    carrFechas = preparaFechas(list((fExamen, fTorneo, fOtro)))
    return render_template("BaseDeDatos/gimnasios.html",
                           carrFechas=carrFechas, listaGims=listaGims,
                           fActual=datetime.now().date(),
                           fExamen=fExamen[0] if fExamen else fExamen,
                           fTorneo=fTorneo[0] if fTorneo else fTorneo,
                           fOtro=fOtro[0] if fOtro else fOtro)


@app.route("/Teoria")
def teoria():
    fExamen = fechaEventoProx("Examen")
    fTorneo = fechaEventoProx("Torneo",)
    fOtro = fechaEventoProx("Otros eventos")
    carrFechas = preparaFechas(list((fExamen, fTorneo, fOtro)))
    return render_template("BaseDeDatos/teoria.html",
                           carrFechas=carrFechas, fActual=datetime.now().date(),
                           fExamen=fExamen[0] if fExamen else fExamen,
                           fTorneo=fTorneo[0] if fTorneo else fTorneo,
                           fOtro=fOtro[0] if fOtro else fOtro)


@app.route("/Base")
def inicio():
    usuarios = Usuario.query.all()
    if len(usuarios) == 0:
        return redirect(url_for('agregar_usuario', msj="Super"))
    if "E-Mail" not in session:
        return redirect(url_for("login"))
    if tiempoSesion():
        return redirect(url_for("logout"))
    notificaciones = (motor.connect().execute(select(
        Notificaciones.id_notificacion, Notificaciones.notificacion
    ).filter(Notificaciones.id_notificacion.in_(
        select(usuNoti.id_Notificacion).filter(
        usuNoti.id_Usuario == session["id"]
        )
    )).order_by(Notificaciones.id_notificacion.desc()))).fetchall()
    gimnasios = False
    if session["Cargo"] == 'Administrador':
        if Gimnasio.query.limit(1):
            gimnasios = True
    else:
        if usuGim.query.filter_by(id_usuario=session["id"]).first() or usuGim.query.filter_by(id_cabeza=session["id"]).first():
            gimnasios = True
    return render_template("BaseDeDatos/Inicio_base.html", msj=session["Cargo"],
                           notificaciones=notificaciones, usuario=session["id"], gimnasios=gimnasios)

@app.route("/contra/<int:id>")
def contra(id):
    obj = {}
    obj["msj"] = (Usuario.query.get(id)).contraseña_usuario
    return jsonify({'lista': obj})


@app.route("/login", methods={"GET", "POST"})
def login():
    if request.form.getlist("reto"):
        return redirect(url_for("base"))
    if request.method == "POST":
        validar_usuario = Usuario.query.filter_by(
            email_usuario=request.form["E-Mail"], contraseña_usuario=request.form["password"]).first()
        if validar_usuario:
            session["E-Mail"] = validar_usuario.email_usuario
            session["Cargo"] = validar_usuario.cargo_usuario
            session["id"] = validar_usuario.id_usuario
            flask.permanent = True
            flask.modified = True
            session["tiempo"] = datetime.utcnow() + timedelta(hours=ESPERA)
            return redirect(url_for("inicio"))
        return render_template("BaseDeDatos/login.html", msj="Error al ingresar los datos")
    return render_template("BaseDeDatos/login.html")


def tiempoSesion():
    if session["tiempo"] and session["tiempo"].replace(tzinfo=None) < datetime.utcnow():
        return True
    session["tiempo"] = datetime.utcnow() + timedelta(hours=ESPERA)
    return False


@app.route("/logout")
def logout():
    session.pop("E-Mail")
    session.pop("Cargo")
    session.pop("id")
    session.pop("tiempo")
    return redirect(url_for("inicio"))

# Notificaciones


@app.route("/crear_notificacion", methods={'GET', 'POST'})
def crear_notificacion():
    if tiempoSesion():
        return redirect(url_for("logout"))
    notificacion = Notificaciones()
    notiForm = NotificacionForm(obj=notificacion)
    usuarios = Gimnasio_Usuario()
    if request.method == 'POST':
        if notiForm.validate_on_submit():
            with motor.connect() as con:
                idNoti = con.execute(insert(Notificaciones).values(
                    notificacion=notiForm.notificacion._value(),
                    asunto=notiForm.asunto.data
                )).inserted_primary_key[0]
                if usuarios.usuario.data == "Nada":
                    usu = Usuario.query.with_entities(
                        Usuario.id_usuario
                    ).all()
                    for i in usu:
                        con.execute(
                            insert(usuNoti).values(
                                id_Usuario=i.id_usuario,
                                id_Notificacion=idNoti
                            )
                        )
                else:
                    con.execute(
                        insert(usuNoti).values(
                            id_Usuario=usuarios.usuario.data,
                            id_Notificacion=idNoti
                        )
                    )
            return redirect(url_for('inicio'))
    usuario = Usuario.query.with_entities(
        Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
    ).all()
    usuarios.usuario.choices.append((f'Nada', f'Todos los usuarios'))
    for idUsu, nom, ape in usuario:
        usuarios.usuario.choices.append((f'{idUsu}', f'{nom} {ape}'))
    return render_template("BaseDeDatos/crear_notificaciones.html", forma=notiForm,
                           usuarios=usuarios)


@app.route("/elimNoti/<int:idNoti>")
def elimNoti(idNoti):
    with motor.connect() as con:
        con.execute(delete(usuNoti).filter(
            usuNoti.id_Notificacion == idNoti,
            usuNoti.id_Usuario == session["id"]
        ))
        if not (con.execute(select(1).filter(
            usuNoti.id_Notificacion == idNoti
        ))).fetchall():
            con.execute(delete(Notificaciones).filter(
                Notificaciones.id_notificacion == idNoti
            ))

# Inicio de funciones de usuarios


@app.route("/editar_usuario/<int:id>/<string:opc>", methods={'GET', 'POST'})
@app.route("/editar_usuario/ver_usuarios")
def editar_usuario(id, opc):
    if tiempoSesion():
        return redirect(url_for("logout"))
    usuario = Usuario.query.get_or_404(id)
    usuarioForma = UsuarioForm(obj=usuario)
    cabezas = Usuario.query.filter(
        Usuario.cargo_usuario == "Cabeza"
    ).with_entities(
        Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
    ).all()
    usuarios = Usuario.query.filter(Usuario.id_usuario.in_(
        usuGim.query.group_by(
            usuGim.id_usuario).with_entities(usuGim.id_usuario)
    ), Usuario.id_usuario != id
    ).with_entities(Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario).all()
    if request.method == 'POST':
        usuarioForma.populate_obj(usuario)
        usuario.ordenarDatos(request.form.get("cabeza"),
                             request.form.get("instructor"), "")
        db.session.commit()
        if session["Cargo"] == 'Usuario':
            return redirect(url_for("inicio"))
        if opc == "editar":
            return redirect(url_for("ver_usuarios", opc="todo"))
        return redirect(url_for("inicio"))
    return render_template("BaseDeDatos/Usuarios/editar_usuario.html", forma=usuarioForma,
                           cabezas=cabezas, msj=opc, usuarios=usuarios,
                           usuario=False if session["Cargo"] == "Usuario" else True)


@app.route("/eliminar_usuario/<int:id>")
def eliminar_usuario(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    with motor.connect() as con:
        con.execute(delete(usuNoti).filter(usuNoti.id_Usuario == id))
        con.execute(delete(Notificaciones).filter(Notificaciones.id_notificacion.notin_(
            usuNoti.query.with_entities(usuNoti.id_Notificacion).group_by(usuNoti.id_Notificacion)
            )))
        desaGims(usuGim.query.filter(usuGim.id_usuario ==
                 id).with_entities(usuGim.id_UsuGim))
        con.execute(update(Usuario).filter(Usuario.id_cabeza == id).values(id_cabeza = None))
        con.execute(update(Usuario).filter(Usuario.instructor == id).values(instructor = None))
        con.execute(delete(Usuario).filter(Usuario.id_usuario == id))
    return redirect(url_for("ver_usuarios", opc='todo'))


@app.route("/agregar_usuario/<string:msj>", methods={'GET', 'POST'})
def agregar_usuario(msj):
    if msj != 'Super' and tiempoSesion():
        return redirect(url_for("logout"))
    usuario = Usuario()
    usuarioForm = UsuarioForm(obj=usuario)
    cabezas = Usuario.query.filter(
        Usuario.cargo_usuario == "Cabeza"
    ).with_entities(
        Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
    ).all()
    usuarios = Usuario.query.filter(Usuario.id_usuario.in_(
        usuGim.query.group_by(
            usuGim.id_usuario).with_entities(usuGim.id_usuario)
    )).with_entities(Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario).all()
    cabezas.insert(0, (0, "", ""))
    usuarios.insert(0, (0, "", ""))
    if request.method == 'POST':
        usuarioForm.populate_obj(usuario)
        usuario.ordenarDatos(request.form.get("cabeza"),
                             request.form.get("instructor"), "Taekwondo")
        db.session.add(usuario)
        if usuario.instructor == 0:
            usuario.instructor = usuario.id_usuario
        if usuario.id_cabeza == 0:
            usuario.id_cabeza = usuario.id_usuario
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template("BaseDeDatos/Usuarios/agregar_usuario.html",
                           forma=usuarioForm, cabezas=cabezas, msj=msj, usuarios=usuarios)


@app.route("/mostrarUsu/<int:idUsu>")
def mostrarUsu(idUsu):
    with motor.connect() as con:
        usuario = con.execute(select(
            Usuario.apellido_usuario, Usuario.nombre_usuario, Usuario.documento_usuario,
            Usuario.email_usuario, Usuario.categoria, Usuario.cargo_usuario
        ).filter(Usuario.id_usuario == idUsu)).fetchone()
        instructor = con.execute(select(
            Usuario.apellido_usuario, Usuario.nombre_usuario
        ).filter(
            Usuario.id_usuario == (select(Usuario.instructor).filter(
            Usuario.id_usuario == idUsu
            ))
        )).fetchone()
        cabeza = con.execute(select(
            Usuario.apellido_usuario, Usuario.nombre_usuario
        ).filter(
            Usuario.id_usuario == (select(Usuario.id_cabeza).filter(
            Usuario.id_usuario == idUsu
            ))
        )).fetchone()
        gimnasio = select(
            Gimnasio.nombre_gimnasio, Gimnasio.direccion_gimnasio
        )
        if session["Cargo"] == "Cabeza":
            gimnasio = gimnasio.filter(
                Gimnasio.id_gimnasio.in_(select(usuGim.id_gimnasio).filter(
                usuGim.id_cabeza == idUsu
                ).group_by(usuGim.id_gimnasio)))
        else:
            gimnasio = gimnasio.filter(
                Gimnasio.id_gimnasio.in_(select(usuGim.id_gimnasio).filter(
                usuGim.id_usuario == idUsu
                )))
        gimnasio = con.execute(gimnasio).fetchall()
    dirGims = []
    nomGims = []
    for nomGim, dirGim in gimnasio:
        dirGims.append(dirGim)
        nomGims.append(nomGim)
    return jsonify({
        'usuario': list(usuario),
        'instructor': f'{instructor.apellido_usuario} {instructor.nombre_usuario}' if instructor else "Sin instructor",
        'cabeza': f'{cabeza.apellido_usuario} {cabeza.nombre_usuario}' if cabeza else "Sin cabeza de grupo",
        'nomGims': nomGims if nomGims else None,
        'dirGims': dirGims if dirGims else None
        })

@app.route("/contraUsu/<int:idUsu>")
def contraUsu(idUsu):
    contra = motor.connect().execute(select(Usuario.contraseña_usuario).filter(
        Usuario.id_usuario == idUsu
    )).fetchone()
    return jsonify({
        'contra': list(contra)
    })


@app.route("/ver_usuarios/<string:opc>")
def ver_usuarios(opc):
    if tiempoSesion():
        return redirect(url_for("logout"))
    usuarios = []
    if opc == 'todo':
        usuarios = Usuario.query.with_entities(
            Usuario.nombre_usuario, Usuario.apellido_usuario,
            Usuario.cargo_usuario, Usuario.id_usuario
        ).all()
    elif opc == 'cabeza':
        usuarios = Usuario.query.filter(
            Usuario.cargo_usuario == "Cabeza"
        ).with_entities(
            Usuario.nombre_usuario, Usuario.apellido_usuario,
            Usuario.cargo_usuario, Usuario.id_usuario
        ).all()
    elif opc == 'instructor':
        usuarios = Usuario.query.filter(or_(Usuario.cargo_usuario == "Cabeza",
                                            Usuario.cargo_usuario == "Usuario")
                                        ).with_entities(
            Usuario.nombre_usuario, Usuario.apellido_usuario,
            Usuario.cargo_usuario, Usuario.id_usuario
        ).all()
    elif opc == 'usuario':
        usuarios = Usuario.query.filter(
            Usuario.cargo_usuario == "Usuario"
        ).with_entities(
            Usuario.nombre_usuario, Usuario.apellido_usuario,
            Usuario.cargo_usuario, Usuario.id_usuario
        ).all()
    elif opc == 'administrador':
        usuarios = Usuario.query.filter(
            Usuario.cargo_usuario == "Administrador"
        ).with_entities(
            Usuario.nombre_usuario, Usuario.apellido_usuario,
            Usuario.cargo_usuario, Usuario.id_usuario
        ).all()
    return render_template("BaseDeDatos/Usuarios/ver_usuarios.html", usuarios=usuarios)


@app.route("/cambiar_contraseña/<string:msj>", methods={'GET', 'POST'})
def cambiar_contraseña(msj):
    if tiempoSesion():
        return redirect(url_for("logout"))
    if request.method == 'POST':
        contra1 = request.form.getlist("contra_1")[0]
        contra2 = request.form.getlist("contra_2")[0]
        if contra1 and contra2 and contra1 == contra2:
            if (Usuario.query.get(session["id"])).contraseña_usuario == contra1:
                return render_template("BaseDeDatos/Usuarios/cambiar_contraseña.html", msj='La contraseña ingresada es igual a la contraseña del usuario')
            with motor.connect() as con:
                con.execute(update(Usuario).filter(
                    Usuario.id_usuario == session["id"]
                ).values(
                    contraseña_usuario=contra1
                ))
            return redirect(url_for('inicio'))
        else:
            return render_template("BaseDeDatos/Usuarios/cambiar_contraseña.html", msj='Verifique los datos ingresados')
    return render_template("BaseDeDatos/Usuarios/cambiar_contraseña.html", msj='nada')


@app.route("/cabezas")
def cabezas():
    if tiempoSesion():
        return redirect(url_for("logout"))
    cabezas = Usuario.query.filter(
        Usuario.cargo_usuario == "Cabeza"
    ).with_entities(
        Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
    ).all()
    listaUsuarios = []
    for id, nom, ape in cabezas:
        usuarioObj = {}
        usuarioObj["id"] = id
        usuarioObj["Nombre"] = nom
        usuarioObj["Apellido"] = ape
        listaUsuarios.append(usuarioObj)
    return jsonify({'lista': listaUsuarios})

# Fin de funciones usuario

# Inicio de las funciones de eventos


@app.route("/editar_evento/<int:id>", methods={'GET', 'POST'})
def editar_evento(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    evento = Eventos.query.get_or_404(id)
    eventoForma = ExamenForm(obj=evento)
    gimnasios = Usuario_Gimnasio()
    gimnasio = Gimnasio.query.with_entities(
        Gimnasio.id_gimnasio, Gimnasio.nombre_gimnasio, Gimnasio.direccion_gimnasio
    ).all()
    for idGim, nom, dir in gimnasio:
        gimnasios.gimnasio.choices.append((f'{idGim}', f'{nom} {dir}'))
    gimnasios.gimnasio.choices.append(('otro', 'Otro lugar'))
    if request.method == 'POST' and eventoForma.validate_on_submit():
        eventoForma.populate_obj(evento)
        evento.lugar_evento = (Gimnasio.query.get(
            gimnasios.gimnasio.data)).nombre_gimnasio
        db.session.commit()
        return redirect(url_for("ver_eventos", opc="todo"))
    return render_template("BaseDeDatos/Eventos/editar_evento.html", forma=eventoForma, formaGim=gimnasios)


@app.route("/eliminar_evento/<int:id>")
def eliminar_evento(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    with motor.connect() as con:
        direc = Imagen.query.filter(
            Imagen.id_evento == id
        ).with_entities(Imagen.direccion).all()
        for i in direc:
            url = pathlib.Path('Base/static/' + i.direccion)
            url.unlink()
        con.execute(delete(Imagen).filter(
            Imagen.id_evento == id
        ))
        con.execute(delete(aluEven).filter(
            aluEven.id_evento == id
        ))
        con.execute(delete(Eventos).filter(
            Eventos.id_evento == id
        ))
    return redirect(url_for("ver_eventos", opc="todo"))


@app.route("/agregar_evento", methods={'GET', 'POST'})
def agregar_evento():
    if tiempoSesion():
        return redirect(url_for("logout"))
    evento = Eventos()
    eventoForma = ExamenForm(obj=evento)
    registro_gimnasio = Usuario_Gimnasio()
    gimnasios = Gimnasio.query.with_entities(
        Gimnasio.id_gimnasio, Gimnasio.nombre_gimnasio, Gimnasio.direccion_gimnasio
    ).all()
    for idGim, nom, dir in gimnasios:
        registro_gimnasio.gimnasio.choices.append((f'{idGim}', f'{nom} {dir}'))
    registro_gimnasio.gimnasio.choices.append(('otro', 'Otro lugar'))
    if request.method == 'POST' and eventoForma.validate_on_submit():
        eventoForma.populate_obj(evento)
        if registro_gimnasio.gimnasio.data == 'otro':
            evento.lugar_evento = None
        else:
            evento.lugar_evento = (Gimnasio.query.get(
                registro_gimnasio.gimnasio.data)).nombre_gimnasio
        db.session.add(evento)
        db.session.commit()
        return redirect(url_for('inicio'))
    return render_template("BaseDeDatos/Eventos/agregar_evento.html", forma=eventoForma,
                           formaGim=registro_gimnasio)

@app.route("/mostrarEven/<int:idEven>")
def mostrarEven(idEven):
    with motor.connect() as con:
        even = con.execute(select(Eventos).filter(
            Eventos.id_evento == idEven
        )).fetchone()
        alusEven = select(
            Alumno.apellido_alumno, Alumno.nombre_alumno
            ).filter(
            Eventos.id_evento == idEven, Eventos.id_evento == aluEven.id_evento,
            aluEven.id_alumno == Alumno.id_alumno
        )
        if session["Cargo"] == "Usuario":
            alusEven = alusEven.filter(
                Alumno.id_UsuGim == usuGim.id_UsuGim,
                usuGim.id_usuario == session["id"]
            )
        elif session["Cargo"] == "Cabeza":
            alusEven = alusEven.filter(
                Alumno.id_UsuGim == usuGim.id_UsuGim,
                usuGim.id_cabeza == session["id"]
            )
        alusEven = con.execute(alusEven).fetchall()
    alusNomApe = [aluApe + " " + aluNom for aluApe, aluNom in alusEven]
    return jsonify({
        'evento': list(even),
        'diaEven': f'{even.fecha_evento.day}/{even.fecha_evento.month}/{even.fecha_evento.year}',
        'alus': alusNomApe
    })


@app.route("/ver_eventos/<string:opc>", methods={'GET', 'POST'})
def ver_eventos(opc):
    if tiempoSesion():
        return redirect(url_for("logout"))
    examenes = []
    torneos = []
    otros = []
    if opc == "examen":
        examenes = Eventos.query.filter_by(tipo_de_evento='Examen').all()
    elif opc == "torneos":
        torneos = Eventos.query.filter_by(tipo_de_evento='Torneo').all()
    elif opc == "otros":
        otros = Eventos.query.filter_by(tipo_de_evento="Otros eventos").all()
    else:
        otros = Eventos.query.filter_by(tipo_de_evento="Otros eventos").all()
        examenes = Eventos.query.filter_by(tipo_de_evento='Examen').all()
        torneos = Eventos.query.filter_by(tipo_de_evento='Torneo').all()
    if request.method == 'POST':
        fDesde = request.form.get('fDesde') if request.form.get(
            'fDesde') else date.min
        fHasta = request.form.get('fHasta') if request.form.get(
            'fHasta') else date.max
        if fDesde or fHasta:
            if opc == "examen":
                examenes = filtarFechasEvento(fDesde, fHasta, "Examen")
            elif opc == "torneos":
                torneos = filtarFechasEvento(fDesde, fHasta, "Torneos")
            elif opc == "otros":
                otros = filtarFechasEvento(fDesde, fHasta, "Otros eventos")
            else:
                otros = filtarFechasEvento(fDesde, fHasta, "Otros eventos")
                torneos = filtarFechasEvento(fDesde, fHasta, "Torneo")
                examenes = filtarFechasEvento(fDesde, fHasta, "Examen")
    return render_template("BaseDeDatos/Eventos/ver_eventos.html", examenes=examenes,
                           torneos=torneos, otros=otros, msj=session["Cargo"], opc=opc)


def filtarFechasEvento(fDesde, fHasta, tipo):
    return Eventos.query.filter(
        Eventos.fecha_evento >= fDesde, Eventos.fecha_evento <= fHasta, Eventos.tipo_de_evento == tipo
    ).all()

# Fin de las funciones de eventos

# Inicio de las funciones de gimnasios


@app.route("/quitar_usuarios/<int:id>", methods={'GET', 'POST'})
def quitar_usuarios(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    registros = []
    if session["Cargo"] == "Administrador":
        registros = usuGim.query.filter(
            usuGim.id_gimnasio == id
        ).with_entities(
            usuGim.id_usuario
        )
    elif session["Cargo"] == "Cabeza":
        registros = usuGim.query.filter(
            usuGim.id_gimnasio == id, usuGim.id_cabeza == session["id"]
        ).with_entities(
            usuGim.id_usuario
        )
    usuarios = Usuario.query.filter(
        Usuario.id_usuario.in_(registros)
    ).with_entities(
        Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
    ).all()
    if request.method == 'POST':
        desaGims(usuGim.query.filter(
            usuGim.id_usuario.in_(request.form.getlist("checkbox")),
            usuGim.id_gimnasio == id
        ).with_entities(usuGim.id_UsuGim))
        return redirect(url_for('ver_gimnasios', opc="todo"))
    return render_template("BaseDeDatos/Gimnasios/quitar_usuarios.html",
                           usuarios=usuarios, idGim=id)


@app.route("/agregar_usuarios/<int:id>", methods={'GET', 'POST'})
def agregar_usuarios(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    usuarioForm = []
    usuarios = Usuario.query
    usuarios = usuarios.filter(
        Usuario.cargo_usuario != "Administrador"
        ) if session["Cargo"] == "Administrador" else usuarios.filter(or_(
        Usuario.id_cabeza == session["id"],
        Usuario.id_usuario == session["id"]
        ))
    usuarios = usuarios.with_entities(
        Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
    ).all()
    for idUsu, nom, ape in usuarios:
        regis = usuGim.query.filter(
            usuGim.id_usuario == idUsu, usuGim.id_gimnasio == id
        ).with_entities(
            usuGim.id_cabeza
        ).first()
        if not regis:
            usuarioForm.append((idUsu, nom, ape))
    if request.method == 'POST':
        seleccion = request.form.getlist("checkbox")
        gimnasio = Gimnasio.query.get(id)
        if seleccion:
            for i in seleccion:
                usu = Usuario.query.get(i)
                armarUsuGim(i, id, usu.id_cabeza)
                os.mkdir(pathlib.Path(
                    f'Base/static/Imagenes/{(gimnasio.nombre_gimnasio).replace(" ","")}/{usu.nombre_usuario}_{usu.apellido_usuario}'))
        return redirect(url_for('ver_gimnasios', opc="todo"))
    return render_template("BaseDeDatos/Gimnasios/agregar_usuarios.html",
                           usuarioForm=usuarioForm, idGim=id)


@app.route("/editar_gimnasio/<int:id>", methods={'GET', 'POST'})
def editar_gimnasio(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    msj = "Usuario"
    if session["Cargo"] == "Administrador" or session["Cargo"] == "Cabeza":
        msj = "Administrador"
    gimnasio = Gimnasio.query.get_or_404(id)
    gimnasioForma = GimnasioForm(obj=gimnasio)
    if request.method == 'POST':
        gimnasioForma.populate_obj(gimnasio)
        gimnasio.capitalizarGim()
        if request.files['foto']:
            url = pathlib.Path('Base/static/' + gimnasio.logo_gimnasio)
            url.unlink()
            nombre = photos.save(
                request.files['foto'], f'{gimnasio.nombre_gimnasio.replace(" ","")}')
            gimnasio.armarGim(
                "Imagenes/" + (url_for('obtener_nombre', filename=nombre)[9:]))
        db.session.commit()
        return redirect(url_for("ver_gimnasios", opc="todo"))
    return render_template("BaseDeDatos/Gimnasios/editar_gimnasio.html", forma=gimnasioForma,
                           msj=msj, gimnasio=id)


@app.route("/horarios/<int:id>", methods={'GET', 'POST'})
def horarios(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    usugim = usuGim.query.filter(usuGim.id_gimnasio == id)
    if session["Cargo"] == "Usuario":
        usugim = usugim.filter(usuGim.id_usuario == session["id"])
    usugim = usugim.with_entities(usuGim.id_UsuGim, usuGim.id_usuario).all()
    horarios = []
    for idUsuGim, idUsu in usugim:
        regis = horarioGim.query.filter(
            horarioGim.id_UsuGim == idUsuGim
        ).with_entities(
            horarioGim.idHorario, horarioGim.descripcion
        ).all()
        usu = Usuario.query.get(idUsu)
        for idHora, desc in regis:
            horarios.append(
                [idHora, desc, f'{usu.nombre_usuario} {usu.apellido_usuario}'])
    if request.method == 'POST':
        seleccionados = request.form.getlist("checkbox")
        motor.connect().execute(delete(horarioGim).filter(
            horarioGim.idHorario.in_(seleccionados)
        ))
        horariosGim = request.form.getlist("horariosGimnasio")
        usuarios = request.form.getlist("usuarios")
        for horaDesc, usuId in zip(horariosGim, usuarios, strict=True):
            if horaDesc and usuId:
                motor.connect().execute(insert(horarioGim).values(
                    descripcion=horaDesc,
                    id_UsuGim=(usuGim.query.filter_by(
                        id_gimnasio=id, id_usuario=usuId).first()).id_UsuGim
                ))
        return redirect(url_for("ver_gimnasios", opc="todo"))
    return render_template("BaseDeDatos/Gimnasios/horarios.html", id=id,
                           horarios=horarios)


@app.route("/agregar_gimnasio", methods={'GET', 'POST'})
def agregar_gimnasio():
    if tiempoSesion():
        return redirect(url_for("logout"))
    gimnasio = Gimnasio()
    gimnasioForm = GimnasioForm(obj=gimnasio)
    registro_usuarios = Gimnasio_Usuario()
    if session["Cargo"] == "Administrador":
        usuarios = Usuario.query.filter(or_(
            Usuario.cargo_usuario == "Usuario", Usuario.cargo_usuario == "Cabeza"
        ))
    elif session["Cargo"] == "Cabeza":
        usuarios = Usuario.query.filter(
            Usuario.id_cabeza == session["id"]
        )
    if session["Cargo"] == "Administrador" or session["Cargo"] == "Cabeza":
        usuarios = usuarios.with_entities(
            Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
        ).all()
        for idUsu, nom, ape in usuarios:
            registro_usuarios.usuario.choices.append(
                (f'{idUsu}', f'{nom} {ape}'))
    else:
        registro_usuarios = []
    if request.method == 'POST' and gimnasioForm.validate_on_submit() and request.files['foto']:
        idUsu = registro_usuarios.usuario.data
        gimnasioForm.populate_obj(gimnasio)
        gimnasio.capitalizarGim()
        gim = Gimnasio.query.filter(
            Gimnasio.nombre_gimnasio == gimnasio.nombre_gimnasio,
            Gimnasio.direccion_gimnasio == gimnasio.direccion_gimnasio
        ).first()
        if gim:
            armarUsuGim(idUsu, gim.id_gimnasio,
                        (Usuario.query.get(idUsu)).id_cabeza)
            return redirect(url_for('inicio'))
        nombre = photos.save(
            request.files['foto'], f'{gimnasio.nombre_gimnasio.replace(" ","")}')
        gimnasio.armarGim(
            "Imagenes/" + (url_for('obtener_nombre', filename=nombre)[9:]))
        db.session.add(gimnasio)
        db.session.commit()
        usu = Usuario.query.get(idUsu)
        os.mkdir(
            f'Base/static/Imagenes/{gimnasio.nombre_gimnasio.replace(" ","")}/{usu.nombre_usuario}_{usu.apellido_usuario}')
        if session["Cargo"] == "Administrador" or session["Cargo"] == "Cabeza":
            armarUsuGim(idUsu, gimnasio.id_gimnasio,
                        (Usuario.query.get(idUsu)).id_cabeza)
        else:
            armarUsuGim(session["id"], gim.id_gimnasio,
                        (Usuario.query.get(session["id"])).id_cabeza)
        return redirect(url_for('inicio'))
    return render_template("BaseDeDatos/Gimnasios/agregar_gimnasio.html",
                           forma=gimnasioForm, usuarioForma=registro_usuarios)

@app.route("/mostrarGim/<int:idGim>")
def mostrarGim(idGim):
    with motor.connect() as con:
        usuGims = con.execute(select(
            Usuario.apellido_usuario, Usuario.nombre_usuario
        ).filter(
            Gimnasio.id_gimnasio == idGim,
            Gimnasio.id_gimnasio == usuGim.id_gimnasio,
            usuGim.id_usuario == Usuario.id_usuario
        )).fetchall()
        gimnasio = con.execute(select(
            Gimnasio.nombre_gimnasio, Gimnasio.direccion_gimnasio, Gimnasio.logo_gimnasio
        ).filter(
            Gimnasio.id_gimnasio == idGim
        )).fetchone()
        listAlus = select(
            Alumno.apellido_alumno, Alumno.nombre_alumno
        ).filter(usuGim.id_gimnasio == idGim)
        if session["Cargo"] == "Usuario":
            listAlus = listAlus.filter(usuGim.id_usuario == session["id"])
        elif session["Cargo"] == "Cabeza":
            listAlus = listAlus.filter(usuGim.id_cabeza == session["id"])
        listAlus = listAlus.filter(Alumno.id_UsuGim == usuGim.id_UsuGim).order_by(
            Alumno.apellido_alumno, Alumno.nombre_alumno
        )
        listAlus =con.execute(listAlus).fetchall()
    usuarios = [usuApe + " " + usuNom for usuApe, usuNom in usuGims]
    alumnos = [aluApe + " " + aluNom for aluApe, aluNom in listAlus]
    return jsonify({
        'usuarios': usuarios,
        'gimnasio': list(gimnasio),
        'alumnos': alumnos
    })


@app.route("/eliminar_gimnasio/<string:numGims>/<string:corri>/<string:opc>", methods={"GET", "POST"})
def eliminar_gimnasio(numGims, corri, opc):
    if tiempoSesion():
        return redirect(url_for("logout"))
    if request.method != 'POST':
        listaGims = []
        lista = []
        for i in decodificar(numGims, corri):
            idUsuGim = usuGim.query.filter(
                usuGim.id_gimnasio == i
            )
            usu = Usuario.query.filter(
                Usuario.id_usuario.in_(
                    idUsuGim.with_entities(usuGim.id_usuario))
            ).with_entities(
                Usuario.nombre_usuario, Usuario.apellido_usuario
            ).all()
            idUsuGim = idUsuGim.with_entities(
                usuGim.id_UsuGim, usuGim.id_cabeza).all()
            usuarioGim = []
            usuarioGim.append((Gimnasio.query.get(i)).nombre_gimnasio)
            listaAux = []
            for idUsu, usufil in zip(idUsuGim, usu):
                listaAux.append(
                    (idUsu.id_UsuGim, usufil.nombre_usuario, usufil.apellido_usuario))
            usuarioGim.append(listaAux)
            lista.append(usuarioGim)
        for i in lista:
            listaGims.append(i)
        return render_template("BaseDeDatos/Gimnasios/Eliminar_gimnasio.html", opc=opc,
                               listaGims=listaGims)
    else:
        desaGims(request.form.getlist("seleccion"))
        return redirect(url_for("ver_gimnasios", opc=opc))


@app.route("/ver_gimnasios/<string:opc>", methods={'GET', 'POST'})
def ver_gimnasios(opc):
    if tiempoSesion():
        return redirect(url_for("logout"))
    msj = "Usuario"
    if session["Cargo"] == "Administrador" or session["Cargo"] == "Cabeza":
        msj = "Administrador"
    usuarios = Gimnasio_Usuario()
    usuarios.usuario.choices.append((("Nada"), ("")))
    usuario = []
    if session["Cargo"] == "Administrador":
        usuario = Usuario.query.filter(or_(
            Usuario.cargo_usuario == "Usuario",
            Usuario.cargo_usuario == "Cabeza"
        ))
    if session["Cargo"] == "Cabeza":
        usuario = Usuario.query.filter(
            Usuario.id_cabeza == session["id"]
        )
    if usuario:
        usuario = usuario.with_entities(
            Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
        )
        for idUsu, nom, ape in usuario:
            usuarios.usuario.choices.append((f'{idUsu}', f'{nom} {ape}'))
    gimnasios = []
    if request.method != 'POST':
        if opc == 'todo':
            gimnasios = filtroGims(True, session["id"], False)
        else:
            gimnasios = filtroGims(False, None, False)
    else:
        if opc == 'todo':
            if usuarios.usuario.data != "Nada":
                gimnasios = filtroGims(True, usuarios.usuario.data, True)
            else:
                gimnasios = filtroGims(True, session["id"], False)
        else:
            gimnasios = filtroGims(False, None, False)
    return render_template("BaseDeDatos/Gimnasios/ver_gimnasios.html", gimnasios=gimnasios,
                           usuarios=usuarios, msj=msj, opc=opc)


def filtroGims(habi, idUsu, filtrar):
    registro = []
    if not habi:
        registro = Gimnasio.query.filter(Gimnasio.habilitado == False).with_entities(
            Gimnasio.id_gimnasio
        )
        return idNomDireGim(registro, habi)
    elif filtrar:
        registro = usuGim.query.filter(usuGim.id_usuario == idUsu)
    else:
        if session["Cargo"] == 'Administrador':
            registro = usuGim.query.group_by(usuGim.id_gimnasio)
        elif session["Cargo"] == "Cabeza":
            registro = usuGim.query.filter(usuGim.id_cabeza == idUsu).group_by(
                usuGim.id_gimnasio
            )
        else:
            registro = usuGim.query.filter(usuGim.id_usuario == idUsu)
    return idNomDireGim(registro.with_entities(usuGim.id_gimnasio), habi)


def idNomDireGim(regis, habi):
    regis = Gimnasio.query.filter(
        Gimnasio.id_gimnasio.in_(regis),
        Gimnasio.habilitado == habi
    ).with_entities(
        Gimnasio.id_gimnasio, Gimnasio.nombre_gimnasio, Gimnasio.direccion_gimnasio
    ).all()
    return [(idGim, nom, dire) for idGim, nom, dire in regis]


@app.route("/habiGims/<string:ids>/<string:tams>", methods={'GET', 'POST'})
def habiGims(ids, tams):
    if tiempoSesion():
        return redirect(url_for("logout"))
    listaids = decodificar(ids, tams)
    if session["Cargo"] == 'Usuario':
        usu = Usuario.query.get(session["id"])
        for i in listaids:
            gim = Gimnasio.query.get(i)
            gim.habilitado = True
            db.session.commit()
            armarUsuGim(session["id"], i,
                        (Usuario.query.get(session["id"])).id_cabeza)
            os.mkdir(pathlib.Path
                     (f'Base/static/Imagenes/{gim.nombre_gimnasio.replace(" ","")}/{usu.nombre_usuario}_{usu.apellido_usuario}')
                     )
        return redirect(url_for('ver_gimnasios', opc="todo"))
    else:
        listaGims = []
        listaNoms = Gimnasio_Usuario()
        listaNoms.usuario.choices.append(("Nada", ""))
        usu = []
        if session["Cargo"] == 'Administrador':
            usu = Usuario.query.filter(
                Usuario.cargo_usuario != "Administrador").all()
        else:
            usu = Usuario.query.filter(
                Usuario.id_cabeza == session["id"]).all()
        for i in usu:
            listaNoms.usuario.choices.append(
                (f'{i.id_usuario}', f'{i.nombre_usuario} {i.apellido_usuario}'))
        for i in listaids:
            listaGims.append((Gimnasio.query.get(i)).nombre_gimnasio)
        if request.method == 'POST':
            for sel, opc in zip(request.form.getlist("checkbox"), request.form.getlist("usuario")):
                if opc != "Nada":
                    gim = Gimnasio.query.get(sel)
                    gim.habilitado = True
                    db.session.commit()
                    usu = Usuario.query.get(opc)
                    armarUsuGim(
                        usu.id_usuario, sel, (Usuario.query.get(opc)).id_cabeza)
                    os.mkdir(pathlib.Path
                             (f'Base/static/Imagenes/{gim.nombre_gimnasio.replace(" ","")}/{usu.nombre_usuario}_{usu.apellido_usuario}')
                             )
            return redirect(url_for('ver_gimnasios', opc="todo"))
        return render_template("BaseDeDatos/Gimnasios/HabilitarGims.html",
                               listaids=listaids, listaNoms=listaNoms, listaGims=listaGims, cant=len(listaids))


@app.route("/elimGim/<string:ids>/<string:tams>")
def elimGim(ids, tams):
    if tiempoSesion():
        return redirect(url_for("logout"))
    listaIds = decodificar(ids, tams)
    for i in listaIds:
        gim = Gimnasio.query.get(i)
        url = pathlib.Path("Base/static/" + gim.logo_gimnasio)
        url.unlink()
        os.rmdir(
            f'Base/static/Imagenes/{gim.nombre_gimnasio.replace(" ","")}')
    motor.connect().execute(delete(Gimnasio).filter(
        Gimnasio.id_gimnasio.in_(listaIds)
    ))
    return redirect(url_for("ver_gimnasios", opc="desa"))


@app.route("/desaGim/<string:ids>/<string:tams>")
def desaGim(ids, tams):
    if tiempoSesion():
        return redirect(url_for("logout"))
    desaGims(decodificar(ids, tams))
    return redirect(url_for("ver_gimnasios", opc="todo"))


@app.route("/instructores/<int:id>")
def instructores(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    usugim = usuGim.query.filter(usuGim.id_gimnasio == id)
    if session["Cargo"] == "Usuario":
        usugim = usugim.filter(usuGim.id_usuario == session["id"])
    usugim = usugim.with_entities(usuGim.id_usuario, usuGim.id_UsuGim).all()
    listaUsu = []
    for idUsu,_ in usugim:
        usu = Usuario.query.get(idUsu)
        objTemp = {}
        objTemp["nya"] = f'{usu.nombre_usuario} {usu.apellido_usuario}'
        objTemp["id"] = usu.id_usuario
        listaUsu.append(objTemp)
    return jsonify({'lista': listaUsu})

# Fin de las funciones de gimnasios

# Inicio de funciones de alumnos


@app.route("/mostrar_eventos/<int:id>")
def mostrar_eventos(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    registros = aluEven.query.filter(
        aluEven.id_alumno == id).with_entities(aluEven.id_evento)
    examenes = Eventos.query.filter(Eventos.id_evento.in_(
        registros), Eventos.tipo_de_evento == 'Examen').all()
    torneos = Eventos.query.filter(Eventos.id_evento.in_(
        registros), Eventos.tipo_de_evento == 'Torneo').all()
    otros = Eventos.query.filter(Eventos.id_evento.in_(
        registros), Eventos.tipo_de_evento == 'Otros eventos').all()
    return render_template("BaseDeDatos/Alumnos/mostrar_eventos.html", examenes=examenes,
                           torneos=torneos, otros=otros, alumno=Alumno.query.get(id))


@app.route("/quitar_evento_existente/<int:id>", methods={'GET', 'POST'})
def quitar_evento_existente(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    registros_eventos = aluEven.query.filter(
        aluEven.id_alumno == id).with_entities(aluEven.id_evento)
    registroEventosAlum = Eventos.query.filter(
        Eventos.id_evento.in_(registros_eventos)
    ).with_entities(
        Eventos.id_evento, Eventos.fecha_evento, Eventos.tipo_de_evento
    ).all()
    if request.method == 'POST':
        if request.form.getlist("checkbox"):
            evenPas = cantEventos(id)
            motor.connect().execute(delete(aluEven).filter(
                aluEven.id_alumno == id, aluEven.id_evento.in_(request.form.getlist("checkbox"))
                ))
            evenAct = cantEventos(id)
            if evenPas != evenAct:
                motor.connect().execute(update(Alumno).filter(Alumno.id_alumno == id).values(
                    graduacion_alumno=cambiarCategoria((Alumno.query.get(id)).graduacion_alumno, evenAct - evenPas),
                    fecha_Exa_Desa=ultExa(id)
                    ))
        return redirect(url_for('ver_alumnos', opc="todo"))
    return render_template("BaseDeDatos/Alumnos/quitar_evento_existente.html", registros=registroEventosAlum, alumno=Alumno.query.get(id))


@app.route("/agregar_evento_existente/<int:id>", methods={'GET', 'POST'})
def agregar_evento_existente(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    eventosAlu = Eventos.query.filter(
        Eventos.id_evento.notin_(aluEven.query.filter(
        aluEven.id_alumno == id).with_entities(aluEven.id_evento))
        ).all()
    if request.method == 'POST':
        evenPas = cantEventos(id)
        for i in request.form.getlist("checkbox"):
            motor.connect().execute(insert(aluEven).values(
                id_alumno=id,
                id_evento=i
            ))
        evenAct = cantEventos(id)
        if evenPas != evenAct:
            motor.connect().execute(update(Alumno).filter(
                Alumno.id_alumno == id
            ).values(
                fecha_Exa_Desa=ultExa(id),
                graduacion_alumno=cambiarCategoria((Alumno.query.get(id)).graduacion_alumno, evenAct - evenPas)
            ))
        return redirect(url_for('ver_alumnos', opc="todo"))
    return render_template("BaseDeDatos/Alumnos/agregar_evento_existente.html",
                           registros=eventosAlu, alumno=Alumno.query.get(id))

def cantEventos(id):
    return ((motor.connect().execute(select(func.count(Eventos.tipo_de_evento)).filter(
        Eventos.tipo_de_evento == "Examen", Eventos.id_evento.in_(
            aluEven.query.filter(aluEven.id_alumno == id).with_entities(aluEven.id_evento)
            )
        ))).fetchone())[0]

@app.route("/editar_alumno/<int:id>", methods={'GET', 'POST'})
def editar_alumno(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    usuario_gimnasio = Usuario_Gimnasio()
    alumno = Alumno.query.get_or_404(id)
    alumnoForma = AlumnoForm(obj=alumno)
    regis = usuGim.query
    if session["Cargo"] != "Usuario":
        if session["Cargo"] == "Cabeza":
            regis = regis.filter(
                usuGim.id_cabeza == session["id"]
            )
        regis = regis.with_entities(
            usuGim.id_UsuGim, usuGim.id_gimnasio, usuGim.id_usuario
        ).all()
        for idUsuGim, idGim, idUsu in regis:
            usu = Usuario.query.filter(
                Usuario.id_usuario == idUsu
            ).with_entities(Usuario.nombre_usuario, Usuario.apellido_usuario).first()
            usuario_gimnasio.gimnasio.choices.append(
                (f'{idUsuGim}', f'{(Gimnasio.query.get(idGim)).nombre_gimnasio} {usu.nombre_usuario} {usu.apellido_usuario}')
            )
    else:
        regis = regis.filter(
            usuGim.id_usuario == session["id"]
        ).with_entities(
            usuGim.id_UsuGim, usuGim.id_gimnasio
        ).all()
        for idUsuGim, idGim in regis:
            usuario_gimnasio.gimnasio.choices.append(
                (f'{idUsuGim}', f'{(Gimnasio.query.get(idGim)).nombre_gimnasio}'))
    usuario_gimnasio.gimnasio.choices.insert(0, ("Nada", ""))
    if request.method == 'POST' and alumnoForma.validate_on_submit():
        alumnoForma.populate_obj(alumno)
        alumno.aluNomApe()
        alumno.libreta = request.form.getlist("libre")[0]
        if (usu := usuario_gimnasio.gimnasio.data) != "Nada":
            alumno.id_UsuGim = usu
        if request.form.get("opcionFoto") == "Si":
            if request.files["imagenAlumno"] and alumno.foto != "/Base/static/Imagenes/sin_foto.png":
                url = pathlib.Path(alumno.foto[1:])
                url.unlink()
                fotoNuevaAlu(alumno)
            elif request.files["imagenAlumno"] and alumno.foto == "/Base/static/Imagenes/sin_foto.png":
                fotoNuevaAlu(alumno)
            elif not request.files["imagenAlumno"] and alumno.foto != "/Base/static/Imagenes/sin_foto.png":
                url = pathlib.Path(alumno.foto[1:])
                url.unlink()
                alumno.foto = "/Base/static/Imagenes/sin_foto.png"
        db.session.commit()
        return redirect(url_for('ver_alumnos', opc='todo'))
    registro = aluEven.query.filter_by(id_alumno=id).first()
    return render_template("BaseDeDatos/Alumnos/editar_alumno.html", forma=alumnoForma,
                           gimnasios=usuario_gimnasio, registro=registro, id=id)


def fotoNuevaAlu(alumno):
    usugim = usuGim.query.get(alumno.id_UsuGim)
    usu = Usuario.query.get(usugim.id_usuario)
    dirNueva = f'{(Gimnasio.query.get(usugim.id_gimnasio).nombre_gimnasio).replace(" ","")}/{usu.nombre_usuario}_{usu.apellido_usuario}'
    nombre = photos.save(
        request.files['imagenAlumno'], dirNueva)
    alumno.foto = "/Base/static/Imagenes/" + \
        (url_for('obtener_nombre', filename=nombre)[9:])


@app.route("/mostrarAlu/<int:idAlu>")
def mostrarAlu(idAlu):
    with motor.connect() as con:
        alu = con.execute(select(
                    Alumno.nombre_alumno, Alumno.apellido_alumno, Alumno.nacionalidad_alumno,
                    Alumno.documento_alumno, Alumno.telefono_alumno, Alumno.graduacion_alumno,
                    Alumno.observaciones_alumno, Alumno.email_alumno, Alumno.localidad_alumno,
                    Alumno.fecha_nacimiento_alumno, Alumno.foto, Alumno.id_UsuGim
                    ).filter(Alumno.id_alumno == idAlu)).fetchone()
        idUsuGim = con.execute(select(
                    usuGim.id_usuario, usuGim.id_gimnasio, usuGim.id_cabeza
                    ).filter(usuGim.id_UsuGim == alu.id_UsuGim)).fetchone()
        usu = con.execute(select(
                    Usuario.nombre_usuario, Usuario.apellido_usuario
                    ).filter(Usuario.id_usuario == idUsuGim.id_usuario)).fetchone()
        cabeza = con.execute(select(
                    Usuario.nombre_usuario, Usuario.apellido_usuario
                    ).filter(Usuario.id_usuario == idUsuGim.id_cabeza)).fetchone()
        gim = con.execute(select(Gimnasio.nombre_gimnasio
                    ).filter(Gimnasio.id_gimnasio == idUsuGim.id_gimnasio)).fetchone()
        botExa = filtarEventosAlu(idAlu, "Examen", False)
        botTor = filtarEventosAlu(idAlu, "Torneo", False)
        botEve = filtarEventosAlu(idAlu, "Otros eventos", False)
    return jsonify({
            'lista': [
                alu.apellido_alumno + " " + alu.nombre_alumno,
                alu.nacionalidad_alumno, str(alu.documento_alumno),
                str(alu.telefono_alumno), alu.graduacion_alumno,
                alu.observaciones_alumno, alu.email_alumno,
                alu.localidad_alumno,
                f'{alu.fecha_nacimiento_alumno.day}/{alu.fecha_nacimiento_alumno.month}/{alu.fecha_nacimiento_alumno.year}',
                usu.apellido_usuario + " " + usu.nombre_usuario,
                cabeza.apellido_usuario + " " + cabeza.nombre_usuario,
                gim.nombre_gimnasio
                ], 'foto': alu.foto,
            'mensajes': [
                "Nombre: ", "Nacionalidad: ", "Documento: ",
                "Telefono: ", "Categoria: ", "Observaciones: ",
                "Correo: ", "Localidad: ", "Fecha de nacimiento: ",
                "Instructor: ", "Cabeza de grupo: ", "Lugar de practica: "
            ],
            'botones': [botExa, botTor, botEve],
            'matris': session["Cargo"] == "Administrador"
        })

@app.route("/aluMatris/<int:idAlu>")
def aluMatris(idAlu):
    with motor.connect() as con:
        fetra = con.execute(select(Matriculas.fecha).filter(
            Matriculas.id_Alumno == idAlu,
            Matriculas.tipo == "FETRA"
        ).order_by(Matriculas.fecha.desc())).fetchone()
        aatee = con.execute(select(Matriculas.fecha).filter(
            Matriculas.id_Alumno == idAlu,
            Matriculas.tipo == "AATEE"
        ).order_by(Matriculas.fecha.desc())).fetchone()
        enat = con.execute(select(Matriculas.fecha).filter(
            Matriculas.id_Alumno == idAlu,
            Matriculas.tipo == "ENAT"
        ).order_by(Matriculas.fecha.desc())).fetchone()
    return jsonify({
        'fFetra': f'{fetra.fecha.day}/{fetra.fecha.month}/{fetra.fecha.year}' if fetra else "Sin registro",
        'fAatee': f'{aatee.fecha.day}/{aatee.fecha.month}/{aatee.fecha.year}' if aatee else "Sin registro",
        'fEnat': f'{enat.fecha.day}/{enat.fecha.month}/{enat.fecha.year}' if enat else "Sin registro"
    })

@app.route("/matrisAlu/<int:idAlu>/<string:tipo>")
def matrisAlu(idAlu, tipo):
    matris = motor.connect().execute(select(Matriculas.fecha).filter(
        Matriculas.id_Alumno == idAlu, Matriculas.tipo == tipo
    )).fetchall()
    matris = [f'{fMatri[0].day}/{fMatri[0].month}/{fMatri[0].year}' for fMatri in matris]
    return jsonify({
        'matris': matris
    })

@app.route("/modiMatris/<int:idAlu>/<string:tipo>/<string:modo>")
def modiMatris(idAlu,tipo,modo):
    matris = motor.connect().execute(select(
        Matriculas.id_matricula, Matriculas.fecha, Matriculas.tipo
        ).filter(
        Matriculas.id_Alumno == idAlu, Matriculas.tipo == tipo
        )).fetchall()
    return render_template("/BaseDeDatos/Alumnos/modiMatris.html",
                           matris = matris, modo = modo, idAlu = idAlu)

@app.route("/agregaMatris/<string:fechas>/<string:tipo>/<int:idAlu>")
def agregaMatris(fechas, tipo, idAlu):
    listafechas = strAdate(fechas.split("n"))
    with motor.connect() as con:
        for elem in listafechas:
            if elem <= date.today() and not con.execute(
                select(Matriculas.id_matricula).filter(
                Matriculas.id_Alumno == idAlu, Matriculas.fecha == elem,
                Matriculas.tipo == tipo
                )
            ).fetchone():
                con.execute(insert(Matriculas).values(
                    id_Alumno = idAlu, fecha = elem, tipo = tipo
                ))
                con.commit()
    return jsonify()

def strAdate(lista):
    return [date(int(elem[0:4]),int(elem[5:7]),int(elem[8:])) for elem in lista]

@app.route("/editaMatris/<string:ids>/<string:fechas>/<string:tipo>/<int:idAlu>")
def editaMatris(ids, fechas, tipo, idAlu):
    fechas = strAdate(fechas.split("n"))
    ids = strAint(ids.split("n"))
    with motor.connect() as con:
        for idMatri, fechaMatri in zip(ids, fechas):
            if not (con.execute(select(Matriculas.id_matricula).filter(
                Matriculas.fecha == fechaMatri, Matriculas.id_Alumno == idAlu,
                Matriculas.tipo == tipo
            ))).fetchall():
                con.execute(update(Matriculas).filter(
                    Matriculas.id_matricula == idMatri
                ).values(
                    fecha = fechaMatri
                ))
                con.commit()
    return jsonify()

@app.route("/elimMatris/<string:ids>")
def elimMatris(ids):
    ids = strAint(ids.split("n"))
    with motor.connect() as con:
        con.execute(delete(Matriculas).filter(
            Matriculas.id_matricula.in_(ids)
        ))
        con.commit()
    return jsonify()

def strAint(lista):
    return [int(elem) for elem in lista]
        
@app.route("/eventosAlu/<int:idAlu>/<string:tipo>")
def eventosAlu(idAlu,tipo):
    fechas = []
    lugares = []
    eventos = filtarEventosAlu(idAlu, tipo, True)
    for fech, lug, lugOpc in eventos:
        fechas.append(f'{fech.day}/{fech.month}/{fech.year}')
        lugares.append(lugOpc if lugOpc else lug)
    return jsonify({'fechas': fechas, 'lugares': lugares})

def filtarEventosAlu(idAlu,tipo, multi):
    resu = motor.connect().execute(select(
        Eventos.fecha_evento, Eventos.lugar_evento, Eventos.lugarOpc).filter(
        Eventos.tipo_de_evento == tipo, Eventos.id_evento.in_(
        select(aluEven.id_evento).filter(
        aluEven.id_alumno == idAlu)))).fetchall()
    if resu and multi:
        return resu
    elif resu and not multi:
        return True
    else:
        return False


@app.route("/agregar_alumno", methods={'GET', 'POST'})
def agregar_alumno():
    if tiempoSesion():
        return redirect(url_for("logout"))
    alumno = Alumno()
    alumnoForm = AlumnoForm(obj=alumno)
    usuarios = Gimnasio_Usuario()
    registros = []
    if session["Cargo"] == 'Administrador':
        registros = usuGim.query.with_entities(
            usuGim.id_UsuGim, usuGim.id_gimnasio, usuGim.id_usuario
        ).all()
    elif session["Cargo"] == "Cabeza":
        registros = usuGim.query.filter(
            or_(usuGim.id_cabeza == session["id"], usuGim.id_cabeza == None)
        ).with_entities(
            usuGim.id_UsuGim, usuGim.id_gimnasio, usuGim.id_usuario
        ).all()
    else:
        registros = usuGim.query.filter(
            usuGim.id_usuario == session["id"]
        ).with_entities(
            usuGim.id_UsuGim, usuGim.id_gimnasio, usuGim.id_usuario
        ).all()
    for idUsuGim, idGim, idUsu in registros:
        j = Gimnasio.query.filter(
            Gimnasio.id_gimnasio == idGim
        ).with_entities(
            Gimnasio.nombre_gimnasio
        ).first()
        k = Usuario.query.filter(
            Usuario.id_usuario == idUsu
        ).with_entities(
            Usuario.nombre_usuario, Usuario.apellido_usuario
        ).first()
        usuarios.usuario.choices.append(
            (f'{idUsuGim}', f'{j.nombre_gimnasio} {k.nombre_usuario} {k.apellido_usuario}'))
    if request.method == 'POST':
        resu = Usuario.query.filter(
            Usuario.cargo_usuario == "Administrador"
        ).with_entities(
            Usuario.id_usuario
        )
        nombre = ""
        usugim = usuGim.query.get(usuarios.usuario.data)
        usu = Usuario.query.get(usugim.id_usuario)
        if request.files['foto']:
            nombre = photos.save(
                request.files['foto'], f'{(Gimnasio.query.get(usugim.id_gimnasio).nombre_gimnasio).replace(" ","")}/{usu.nombre_usuario}_{usu.apellido_usuario}')
        with motor.connect() as conn:
            alumnoForm.populate_obj(alumno)
            alumno.libreta = request.form.getlist("libre")[0]
            alumno.armarAlumno(datetime.now().date(), usugim.id_UsuGim,
                               "/Base/static/Imagenes/sin_foto.png" if not nombre else "/Base/static/Imagenes/" + (url_for('obtener_nombre', filename=nombre)[9:]))
            db.session.add(alumno)
            db.session.commit()
            idNoti = conn.execute(insert(Notificaciones).values(
                notificacion=f'Se ha registrado al alumno {alumno.apellido_alumno} {alumno.nombre_alumno}',
            ))
            for i in resu:
                conn.execute(
                    insert(usuNoti).values(
                        id_Notificacion=idNoti.inserted_primary_key[0],
                        id_Usuario=i.id_usuario
                    )
                )
        return redirect(url_for('inicio'))
    return render_template("BaseDeDatos/Alumnos/agregar_alumno.html", forma=alumnoForm, msj=session["Cargo"],
                           usuarios=usuarios)


@app.route("/ver_alumnos/<string:opc>", methods={'GET', 'POST'})
def ver_alumnos(opc):
    if tiempoSesion():
        return redirect(url_for("logout"))
    alumnos = []
    msj = ""
    if session["Cargo"] == "Administrador":
        msj = "Administrador"
    elif session["Cargo"] == "Cabeza":
        msj = "Cabeza"        
    modo = True if opc == "todo" or opc == "habilitado" else False
    libre = True if session["Cargo"] == "Administrador" else False
    form = AlumnoForm()
    opciones = Gimnasio_Usuario()
    opciones.usuario.choices = form.graduacion_alumno.choices
    opciones.usuario.choices.insert(0, ((""), ("")))
    gimnasios = Usuario_Gimnasio()
    gimnasios.gimnasio.choices.append(((""), ("")))
    usuarios = DatoForm()
    regis = usuGim.query
    gim = Gimnasio.query
    if session["Cargo"] != "Usuario":
        usuarios.dato.choices.append(((""), ("")))
        if session["Cargo"] == "Administrador":
            gim = gim.filter(
                Gimnasio.habilitado == True
            )
        else:
            regis = regis.filter(or_(usuGim.id_cabeza == session["id"],usuGim.id_usuario == session["id"]))
            gim = gim.filter(
                Gimnasio.id_gimnasio.in_(
                usuGim.query.filter(usuGim.id_cabeza == session["id"]).with_entities(
                usuGim.id_gimnasio
                ).group_by(usuGim.id_gimnasio)
                )
            )
        regis = Usuario.query.filter(
            Usuario.id_usuario.in_(
                regis.group_by(
                    usuGim.id_usuario
                ).with_entities(
                    usuGim.id_usuario
                )
            )
        ).with_entities(
            Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
        )
        for idUsu, nom, ape in regis.all():
            usuarios.dato.choices.append(((f'{idUsu}'), (f'{nom} {ape}')))
    else:
        regis = regis.filter(
            usuGim.id_usuario == session["id"]
        ).with_entities(
            usuGim.id_gimnasio
        )
        gim = gim.filter(
            Gimnasio.id_gimnasio.in_(regis)
        )

    for idGim, nomGim in gim.with_entities(Gimnasio.id_gimnasio, Gimnasio.nombre_gimnasio).all():
        gimnasios.gimnasio.choices.append(((f'{idGim}'), (f'{nomGim}')))
    if request.method != 'POST':
        if opc == 'todo' or opc == 'habilitado':
            regis = []
            if session["Cargo"] == 'Administrador':
                alumnos = Alumno.query.filter(
                    Alumno.habilitado == True
                )
            elif session["Cargo"] == "Cabeza":
                alumnos = Alumno.query.filter(
                    Alumno.id_UsuGim.in_(
                        usuGim.query.filter(
                            usuGim.id_cabeza == session["id"]
                        ).with_entities(usuGim.id_UsuGim)
                    ))
            else:
                alumnos = Alumno.query.filter(
                    Alumno.id_UsuGim.in_(
                        usuGim.query.filter(
                            usuGim.id_usuario == session["id"]
                        ).with_entities(usuGim.id_UsuGim)
                    ))
                lista = [session["id"]]
                listaIds = []
                while lista != listaIds:
                    listaIds = lista
                    usu = Usuario.query.filter(
                        Usuario.id_usuario.in_(lista)
                    ).with_entities(Usuario.id_usuario, Usuario.id_cabeza).all()
                    for idUsu, _ in usu:
                        lista = [idUsu]
        else:
            alumnos = Alumno.query.filter(
                Alumno.habilitado == False
            )
        alumnos = alumnos.order_by(
            Alumno.apellido_alumno, Alumno.nombre_alumno
        ).with_entities(
            Alumno.id_alumno, Alumno.fecha_Exa_Desa,
            Alumno.libreta, Alumno.apellido_alumno,
            Alumno.nombre_alumno, Alumno.graduacion_alumno
        ).all()
    else:
        regis = []
        alus = Alumno.query.filter(Alumno.habilitado.is_(modo))
        if (nom := request.form.get("Nombre")):
            alus = alus.filter(
                Alumno.nombre_alumno.like(f'%{nom.capitalize()}%'))
        if (ape := request.form.get("Apellido")):
            alus = alus.filter(
                Alumno.apellido_alumno.like(f'%{ape.capitalize()}%'))
        if (cate := opciones.usuario.data):
            alus = alus.filter(Alumno.graduacion_alumno.like(cate))
        if modo:
            regis = usuGim.query
            if (fUsu := usuarios.dato.data) and fUsu != "Nada":
                regis = regis.filter(usuGim.id_usuario == fUsu)
            if (gim := gimnasios.gimnasio.data) and gim != "Nada":
                regis = regis.filter(usuGim.id_gimnasio == gim)
            regis = regis.with_entities(usuGim.id_UsuGim)
        final = []
        if regis and alus:
            final = alus.filter(
                Alumno.id_UsuGim.in_(regis)
            )
        elif alus:
            final = alus
        elif regis:
            final = Alumno.query.filter(
                Alumno.id_UsuGim.in_(regis),
                Alumno.habilitado.is_(modo)
            )
        alumnos = final.order_by(
            Alumno.apellido_alumno, Alumno.nombre_alumno
        ).with_entities(
            Alumno.id_alumno, Alumno.fecha_Exa_Desa,
            Alumno.libreta, Alumno.apellido_alumno,
            Alumno.nombre_alumno, Alumno.graduacion_alumno
        ).all()
    return render_template("BaseDeDatos/Alumnos/ver_alumnos.html", alumnos=alumnos, gimnasios=gimnasios,
                           usuarios=usuarios, msj=msj, modo=modo, opc=opc, opciones=opciones,
                           libre=libre)


@app.route("/libretas/<string:ids>/<string:tams>")
def libretas(ids, tams):
    if tiempoSesion():
        return redirect(url_for("logout"))
    motor.connect().execute(update(Alumno).filter(
        Alumno.id_alumno.in_(decodificar(ids, tams))
    ).values(
        libreta=""
    ))
    return redirect(url_for("ver_alumnos", opc="todo"))


@app.route("/habiAlums/<string:ids>/<string:tams>", methods={'GET', 'POST'})
def habiAlums(ids, tams):
    if tiempoSesion():
        return redirect(url_for("logout"))
    listaids = decodificar(ids, tams)
    if request.method == 'POST':
        gim = request.form.getlist("gimnasio")
        usu = [session["id"]
               for _ in gim] if session["Cargo"] == "Usuario" else request.form.getlist("usuario")
        for idUsu, idGim, idAlu in zip(usu, gim, listaids):
            if idUsu != "Nada" and idGim != "Nada":
                regi = usuGim.query.filter(
                    usuGim.id_usuario == idUsu, usuGim.id_gimnasio == idGim
                ).with_entities(usuGim.id_UsuGim).first()
                alum = Alumno.query.filter(
                    Alumno.id_alumno == idAlu
                ).with_entities(
                    Alumno.foto
                ).first()
                usuario = Usuario.query.get(idUsu)
                dirNueva = f'Base/static/Imagenes/{(Gimnasio.query.get(idGim).nombre_gimnasio).replace(" ","")}/{usuario.nombre_usuario}_{usuario.apellido_usuario}'
                dirAlum = ""
                if alum.foto != "Base/static/Imagenes/sin_foto.png":
                    dirAlum = dirNueva + "/" + \
                        alum.foto[alum.foto.rfind("/") + 1:]
                    shutil.move(alum.foto[1:], dirAlum)
                else:
                    dirAlum = alum.foto
                motor.connect().execute(update(Alumno).filter(
                    Alumno.id_alumno == idAlu
                ).values(
                    habilitado=True,
                    id_UsuGim=regi.id_UsuGim,
                    fecha_Exa_Desa=ultExa(idAlu),
                    foto="/" + dirAlum
                ))
        return redirect(url_for("ver_alumnos", opc="todo"))
    listaAlums = []
    listaGims = []
    msj = True if session["Cargo"] == "Administrador" or session["Cargo"] == "Cabeza" else False
    gimnasio = Usuario_Gimnasio()
    gimnasio.gimnasio.choices.append((f'Nada', f''))
    usuario = Gimnasio_Usuario()
    usuario.usuario.choices.append((f'Nada', f''))
    if session["Cargo"] == "Usuario":
        regis = usuGim.query.filter(
            usuGim.id_usuario == session["id"]
        )
    elif session["Cargo"] == "Cabeza":
        regis = usuGim.query.filter(
            usuGim.id_cabeza == session["id"]
        ).group_by(
            usuGim.id_gimnasio
        )
    else:
        regis = usuGim.query.group_by(
            usuGim.id_gimnasio
        )
    regis = Gimnasio.query.filter(
        Gimnasio.id_gimnasio.in_(regis.with_entities(
            usuGim.id_gimnasio
        ))).with_entities(
            Gimnasio.id_gimnasio, Gimnasio.nombre_gimnasio
    ).all()
    for idGim, nomGim in regis:
        gimnasio.gimnasio.choices.append((f'{idGim}', f'{nomGim}'))
    for _ in listaids:
        listaGims.append(gimnasio)
    alus = Alumno.query.filter(
        Alumno.id_alumno.in_(listaids)
    ).with_entities(
        Alumno.nombre_alumno, Alumno.apellido_alumno
    ).all()
    for nomAlu, apeAlu in alus:
        listaAlums.append((nomAlu, apeAlu))
    return render_template("BaseDeDatos/Alumnos/habilitarAlus.html", msj=msj,
                           listaDatos=zip(listaAlums, listaGims, usuario),
                           listaUsu=zip(listaAlums, listaids, listaGims))


@app.route("/elimAlus/<string:ids>/<string:tams>")
def elimAlus(ids, tams):
    if tiempoSesion():
        return redirect(url_for("logout"))
    listaAlus = decodificar(ids, tams)
    with motor.connect() as con:
        for i in listaAlus:
            alu = Alumno.query.get(i)
            if alu.foto and alu.foto != "/Base/static/Imagenes/sin_foto.png":
                url = pathlib.Path(alu.foto[1:])
                url.unlink()
        con.execute(delete(aluEven).filter(
            aluEven.id_alumno.in_(listaAlus)
        ))
        con.execute(delete(Matriculas).filter(
            Matriculas.id_Alumno.in_(listaAlus)
        ))
        con.execute(delete(Alumno).filter(
            Alumno.id_alumno.in_(listaAlus)
        ))
    return redirect(url_for("ver_alumnos", opc="deshabilitado"))


@app.route("/desaAlum/<string:ids>/<string:tams>")
def desaAlum(ids, tams):
    desaAlums(decodificar(ids, tams), datetime.now().date())
    return redirect(url_for("ver_alumnos", opc="deshabilitado"))


@app.route("/sumarAevento/<string:ids>/<string:tams>/<string:evento>")
def sumarAevento(ids, tams, evento):
    if tiempoSesion():
        return redirect(url_for("logout"))
    eventoReci = Eventos.query.filter(
        Eventos.tipo_de_evento == evento, Eventos.fecha_evento >= datetime.now().date()
    ).order_by(
        Eventos.fecha_evento.asc()
    ).with_entities(
        Eventos.id_evento, Eventos.fecha_evento
    ).first()
    if eventoReci:
        listaIds = decodificar(ids, tams)
        regis = aluEven.query.filter(
            aluEven.id_alumno.notin_(
                select(aluEven.id_alumno).filter(
                    aluEven.id_evento == eventoReci.id_evento
                ).group_by(aluEven.id_alumno)
            ), aluEven.id_alumno.in_(listaIds)
        ).group_by(aluEven.id_alumno).with_entities(aluEven.id_alumno).all()
        alus = Alumno.query
        if not regis:
            alus = alus.filter(Alumno.id_alumno.in_(listaIds))
        else:
            alus = alus.filter(Alumno.id_alumno.in_(regis))
        if evento == "Examen":
            alus = alus.filter(
                or_(Alumno.fecha_Exa_Desa < eventoReci.fecha_evento,
                    Alumno.fecha_Exa_Desa == None)
            )
        alus = alus.with_entities(
            Alumno.id_alumno, Alumno.graduacion_alumno).all()
        with motor.connect() as con:
            for idAlu, _ in alus:
                con.execute(insert(aluEven).values(
                    id_alumno=idAlu,
                    id_evento=eventoReci.id_evento
                ))
            if evento == "Examen":
                for idAlu, cate in alus:
                    con.execute(update(Alumno).filter(
                        Alumno.id_alumno == idAlu
                    ).values(
                        graduacion_alumno=cambiarCategoria(cate, 1),
                        fecha_Exa_Desa=eventoReci.fecha_evento
                    ))
            con.commit()
    return redirect(url_for("ver_alumnos", opc="habilitado"))


def cambiarCategoria(cate, accion):
    pos = CATEGORIAS.index(cate) + accion
    return CATEGORIAS[pos] if pos <= len(CATEGORIAS) else CATEGORIAS[-1]


@app.route("/cambioUsuario/<lugar>")
def cambioUsuario(lugar):
    if tiempoSesion():
        return redirect(url_for("logout"))
    listaUsuarios = []
    regis = {}
    if lugar != "Nada":
        regis = usuGim.query.filter(
            usuGim.id_gimnasio == lugar
        )
    else:
        regis = usuGim.query
    regis = Usuario.query.filter(
        Usuario.id_usuario.in_(
            regis.with_entities(
                usuGim.id_usuario
            ))).with_entities(
        Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
    ).all()
    for idUsu, nom, ape in regis:
        listaUsuarios.append({"id": idUsu, "Nombre": nom, "Apellido": ape})
    return jsonify({'lista': listaUsuarios})


@app.route("/buscarAlumno", methods={'GET', 'POST'})
def buscarAlumno():
    if tiempoSesion():
        return redirect(url_for("logout"))
    alumnosHabi = []
    alumnosDesa = []
    if request.method == 'POST':
        alum = Alumno.query
        if (nom := request.form.get("nombre")):
            alum = alum.filter(
                Alumno.nombre_alumno.like(f'%{nom.capitalize()}%'))
        if (ape := request.form.get("apellido")):
            alum = alum.filter(
                Alumno.apellido_alumno.like(f'%{ape.capitalize()}%'))
        alum = alum.with_entities(
            Alumno.nombre_alumno, Alumno.apellido_alumno,
            Alumno.graduacion_alumno, Alumno.fecha_Exa_Desa,
            Alumno.localidad_alumno, Alumno.id_UsuGim,
            Alumno.habilitado
        ).all()
        for nomAlu, apeAlu, cate, fecha, direc, idUsuGim, habi in alum:
            if habi:
                usugim = usuGim.query.filter(usuGim.id_UsuGim == idUsuGim).with_entities(
                    usuGim.id_usuario, usuGim.id_gimnasio
                ).first()
                usu = Usuario.query.filter(
                    Usuario.id_usuario == usugim.id_usuario
                ).with_entities(Usuario.nombre_usuario, Usuario.apellido_usuario).first()
                alumnosHabi.append([
                    nomAlu, apeAlu, cate, (Gimnasio.query.get(
                        usugim.id_gimnasio)).nombre_gimnasio,
                    f'{usu.nombre_usuario} {usu.apellido_usuario}'
                ])
            else:
                alumnosDesa.append([nomAlu, apeAlu, cate, fecha, direc])
    return render_template("BaseDeDatos/Alumnos/buscarAlumno.html",
                           alumnosHabi=alumnosHabi, alumnosDesa=alumnosDesa)

# Fin de funciones de alumnos

# Matriculas


@app.route("/ver_matriculas/<string:opc>", methods={'GET', 'POST'})
def ver_matriculas(opc):
    if tiempoSesion():
        return redirect(url_for("logout"))
    usuarios = DatoForm()
    usuarios.dato.choices.append(('Nada', ''))
    usu = Usuario.query.filter(
        Usuario.id_usuario.in_(usuGim.query.group_by(
            usuGim.id_usuario
        ).with_entities(usuGim.id_usuario))
    ).with_entities(
        Usuario.id_usuario, Usuario.nombre_usuario, Usuario.apellido_usuario
    ).all()
    for idUsu, nomUsu, apeUsu in usu:
        usuarios.dato.choices.append((f'{idUsu}', f'{nomUsu} {apeUsu}'))
    alumnos = Alumno.query.filter(
        Alumno.habilitado == True
    ).order_by(
        Alumno.apellido_alumno, Alumno.nombre_alumno
    ).all()
    if request.method == 'POST':
        alumnos = []
        registros = []
        if usuarios.dato.data != 'Nada':
            registros = usuGim.query.filter(
                usuGim.id_usuario == usuarios.dato.data
            ).with_entities(usuGim.id_UsuGim)
        alus = Alumno.query
        if (nom := request.form.get("Nombre")):
            alus = alus.filter(
                Alumno.nombre_alumno.like(f'%{nom.capitalize()}%'))
        if (ape := request.form.get("Apellido")):
            Alumno.apellido_alumno.like(f'%{ape.capitalize()}%')
        if registros and alus:
            alumnos = alus.filter(Alumno.id_UsuGim.in_(registros))
        elif alus:
            alumnos = alus
        elif registros:
            alumnos = Alumno.query.filter(Alumno.id_UsuGim.in_(registros))
        else:
            alumnos = Alumno.query.filter(Alumno.habilitado == True)
        alumnos = alumnos.order_by(
            Alumno.apellido_alumno, Alumno.nombre_alumno
        ).all()
    return render_template("BaseDeDatos/Matriculas/ver_matriculas.html", usuarios=usuarios,
                           alumnos=alumnos, opc=opc)


@app.route("/crear/<string:opc>/<string:ids>/<string:tams>")
def crear(opc, ids, tams):
    if tiempoSesion():
        return redirect(url_for("logout"))
    listaIds = decodificar(ids, tams)
    fMatri = date.today()
    alus = select(Alumno.id_alumno).filter(Alumno.id_alumno.in_(listaIds))
    if opc == "AATEE":
        alus = alus.filter(or_(Alumno.fecha_Aatee == None, Alumno.fecha_Aatee != fMatri))
    elif opc == "FETRA":
        alus = alus.filter(or_(Alumno.fecha_Fetra == None, Alumno.fecha_Fetra != fMatri))
    else:
        alus = alus.filter(or_(Alumno.fecha_Enat == None, Alumno.fecha_Enat != fMatri))
    with motor.connect() as con:
        alus = (con.execute(alus)).fetchall()
        if len(alus) == 1:
            alus = alus[0]
        if alus:
            if opc == "AATEE":
                con.execute(update(Alumno).filter(Alumno.id_alumno.in_(alus)
                                                     ).values(fecha_Aatee=fMatri))
            elif opc == "FETRA":
                con.execute(update(Alumno).filter(Alumno.id_alumno.in_(alus)
                                                      ).values(fecha_Fetra=fMatri))
            else:
                con.execute(update(Alumno).filter(Alumno.id_alumno.in_(alus)
                                                     ).values(fecha_Enat=fMatri))
            for idAlu in listaIds:
                armarMatricula(fMatri, opc, idAlu)
                con.execute(update(Alumno).filter(Alumno.id_alumno == idAlu).values(
                    fecha_Aatee=ultMatri(idAlu, "AATEE"), fecha_Enat=ultMatri(idAlu, "ENAT"),
                    fecha_Fetra=ultMatri(idAlu, "FETRA")
                ))
    return redirect(url_for("ver_matriculas", opc="todo"))


def armarMatricula(fecha, tipoMatri, id):
    motor.connect().execute(insert(Matriculas).values(
        tipo=tipoMatri,
        id_Alumno=id,
        fecha=fecha
    ))


@app.route("/Detalles_matriculas/<int:id>")
def Detalles_matriculas(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    return render_template("/BaseDeDatos/Matriculas/Detalles_matriculas.html",
                           matri_AATEE=Matriculas.query.filter_by(
                               tipo="AATEE", id_Alumno=id).all(),
                           matri_ENAT=Matriculas.query.filter_by(
                               tipo="ENAT", id_Alumno=id).all(),
                           matri_FETRA=Matriculas.query.filter_by(tipo="FETRA", id_Alumno=id).all())


@app.route("/Editar_matriculas/<int:id>/<string:modo>", methods={'GET', 'POST'})
def Editar_matriculas(id, modo):
    if tiempoSesion():
        return redirect(url_for("logout"))
    matri_AATEE = Matriculas.query.filter(
        Matriculas.tipo == "AATEE", Matriculas.id_Alumno == id
    ).with_entities(
        Matriculas.id_matricula, Matriculas.fecha
    ).all()
    matri_ENAT = Matriculas.query.filter(
        Matriculas.tipo == "ENAT", Matriculas.id_Alumno == id
    ).with_entities(
        Matriculas.id_matricula, Matriculas.fecha
    ).all()
    matri_FETRA = Matriculas.query.filter(
        Matriculas.tipo == "FETRA", Matriculas.id_Alumno == id
    ).with_entities(
        Matriculas.id_matricula, Matriculas.fecha
    ).all()
    if request.method == 'POST':
        if modo == 'editar':
            modiMatris(request.form.getlist("fecha_AATEE"),
                       request.form.getlist("checkbox_AATEE"))
            modiMatris(request.form.getlist("fecha_ENAT"),
                       request.form.getlist("checkbox_ENAT"))
            modiMatris(request.form.getlist("fecha_FETRA"),
                       request.form.getlist("checkbox_FETRA"))
        else:
            if (seleccion := request.form.getlist("checkbox_FETRA")):
                borrarMatricula(seleccion)
            if (seleccion := request.form.getlist("checkbox_ENAT")):
                borrarMatricula(seleccion)
            if (seleccion := request.form.getlist("checkbox_AATEE")):
                borrarMatricula(seleccion)
        motor.connect().execute(update(Alumno).filter(Alumno.id_alumno == id).values(
            fecha_Aatee=ultMatri(id, "AATEE"), fecha_Enat=ultMatri(id, "ENAT"),
            fecha_Fetra=ultMatri(id, "FETRA")
        ))
        return redirect(url_for("ver_matriculas", opc="todo"))
    return render_template("/BaseDeDatos/Matriculas/Editar_matriculas.html",
                           matri_AATEE=matri_AATEE, matri_ENAT=matri_ENAT,
                           matri_FETRA=matri_FETRA, id=id, modo=modo)


def modiMatris(fechas, ids):
    for idMatri, fMatri in zip(ids, fechas):
        if idMatri and fMatri:
            motor.connect().execute(update(Matriculas).filter(
                Matriculas.id_matricula == idMatri).values(fecha=fMatri))


@app.route("/agregarMatriculas/<int:id>", methods={'GET', 'POST'})
def agregarMatriculas(id):
    if tiempoSesion():
        return redirect(url_for("logout"))
    if request.method == 'POST':
        for i in request.form.getlist("MatriAATEE"):
            armarMatricula(i, 'AATEE', id)
        for i in request.form.getlist("MatriENAT"):
            armarMatricula(i, 'ENAT', id)
        for i in request.form.getlist("MatriFetra"):
            armarMatricula(i, 'FETRA', id)
        motor.connect().execute(update(Alumno).filter(Alumno.id_alumno == id).values(
            fecha_Aatee=ultMatri(id, "AATEE"), fecha_Enat=ultMatri(id, "ENAT"),
            fecha_Fetra=ultMatri(id, "FETRA")
        ))
        return redirect(url_for("ver_matriculas", opc='todo'))
    return render_template("/BaseDeDatos/Matriculas/AgregarMatriculas.html", id=id)

# Imagenes


@app.route("/ver_imagenes/<string:opc>", methods={'GET', 'POST'})
def ver_imagenes(opc):
    if tiempoSesion():
        return redirect(url_for("logout"))
    if request.method == 'POST':
        for i in request.form.getlist("checkboxImagen"):
            dato = Imagen.query.get(i)
            url = pathlib.Path("Base/static/" + dato.direccion)
            url.unlink()
            db.session.delete(dato)
            db.session.commit()
    return render_template("/BaseDeDatos/Imagenes/MostrarImagenes.html",
                           fotoExa=Imagen.query.filter_by(tipo_imagen="Examen").all(
                           ) if opc == "todo" or opc == "Examen" else [],
                           fotoTor=Imagen.query.filter_by(tipo_imagen="Torneo").all(
                           ) if opc == "todo" or opc == "Torneo" else [],
                           fotoAct=Imagen.query.filter_by(tipo_imagen="Otros eventos").all(
                           ) if opc == "todo" or opc == "Otros_eventos" else [])


@app.route("/subir_imagenes/<string:tipo>", methods={'GET', 'POST'})
def subir_imagenes(tipo):
    if tiempoSesion():
        return redirect(url_for("logout"))
    if request.method == 'POST' and request.files:
        if tipo == "Examen" or tipo == "Torneo" or tipo == "Otros_eventos":
            if tipo == "Otros_eventos":
                tipo = "Otros eventos"
            fotos = Imagen.query.filter_by(tipo_imagen=tipo).all()
            for i in fotos:
                url = pathlib.Path("Base/static/" + i.direccion)
                url.unlink()
                db.session.delete(i)
                db.session.commit()
        if tipo == "Aexamen" or tipo == "Atorneo" or tipo == "AOtros_eventos":
            tipo = tipo[1:].capitalize()
        if tipo == "Otros_eventos":
            tipo = "Otros eventos"
        if Eventos.query.filter_by(tipo_de_evento=tipo).first():
            if tipo == "Otros eventos":
                tipo = "Otros_eventos"
            evento = ultimoEvento("Examen") if tipo == "Examen" else ultimoEvento(
                "Torneo") if tipo == "Torneo" else ultimoEvento("Otros eventos")
            for i in request.files.getlist("foto"):
                if i:
                    nombre = photos.save(i, tipo)
                    motor.connect().execute(insert(Imagen).values(
                        direccion="Imagenes" +
                        url_for('obtener_nombre', filename=nombre)[8:],
                        tipo_imagen=tipo if tipo == "Examen" or tipo == "Torneo" else "Otros eventos",
                        id_evento=evento
                    ))
        return redirect(url_for("ver_imagenes", opc="todo"))
    return render_template("/BaseDeDatos/Imagenes/SubirImagenes.html")


@app.route("/uploads/<filename>")
def obtener_nombre(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)


def armarUsuGim(usu, gim, cabeza):
    motor.connect().execute(insert(usuGim).values(
        id_usuario=usu,
        id_gimnasio=gim,
        id_cabeza=cabeza
    ))


def ultExa(alum):
    evento = (motor.connect().execute(select(Eventos.fecha_evento).filter(
        Eventos.tipo_de_evento == "Examen", Eventos.id_evento.in_(
            aluEven.query.filter(aluEven.id_alumno == alum).with_entities(aluEven.id_evento)
            )).order_by(Eventos.fecha_evento.desc()).limit(1)
            )).fetchone()
    if evento:
        return evento.fecha_evento
    else:
        return None


def borrarMatricula(seleccion):
    motor.connect().execute(delete(Matriculas).filter(
        Matriculas.id_matricula.in_(seleccion)
    ))


def ultMatri(id, tipoMatri):
    matriAlum = (motor.connect().execute(select(Matriculas.fecha).filter(
        Matriculas.tipo == tipoMatri, Matriculas.id_Alumno == id
        ).order_by(Matriculas.fecha.desc()).limit(1))).fetchone()
    if matriAlum:
        return matriAlum.fecha
    else:
        return None


def ultimoEvento(tipo):
    return (Eventos.query.filter(
        Eventos.tipo_de_evento == tipo
    ).order_by(
        Eventos.fecha_evento.desc()
    ).first()).id_evento


def decodificar(ids, tams):
    listaIds = []
    tams = list(tams + "0")
    pos = 0
    cont = 0
    while tams[pos] != "0":
        listaIds.append(ids[cont:cont + int(tams[pos])])
        cont += int(tams[pos])
        pos += 1
    return listaIds


def desaAlums(listAlus, fechaDesa):
    if tiempoSesion():
        return redirect(url_for("logout"))
    with motor.connect() as con:
        for id, _ in Alumno.query.filter(
            Alumno.id_alumno.in_(listAlus),
            Alumno.foto != "/Base/static/Imagenes/sin_foto.png"
            ).with_entities(Alumno.id_alumno,Alumno.libreta).all():
            (Alumno.query.get(id)).cambiarFoto("Base/static/Imagenes/Deshabilitados")
            db.session.commit()
        con.execute(update(Alumno).filter(Alumno.id_alumno.in_(listAlus)).values(
            habilitado=False,
            fecha_Exa_Desa=fechaDesa,
            id_UsuGim=None
        ))
        con.commit()


def desaGims(lista):
    gims = usuGim.query
    gims = gims.filter(usuGim.id_UsuGim.in_(lista)) if session["Cargo"] != "Usuario" else gims.filter(
        usuGim.id_usuario == session["id"], usuGim.id_gimnasio.in_(lista))
    with motor.connect() as con:
        for idUsuGim, idgim, idUsu in gims.with_entities(usuGim.id_UsuGim, usuGim.id_gimnasio, usuGim.id_usuario).all():
            listaAlus = []
            for id, _ in Alumno.query.filter(Alumno.id_UsuGim == idUsuGim).with_entities(
                Alumno.id_alumno, Alumno.libreta
                ).all():
                    listaAlus.append(id)
            desaAlums(listaAlus, datetime.now().date())
            con.execute(delete(horarioGim).filter(
                horarioGim.id_UsuGim == idUsuGim
            ))
            con.execute(delete(usuGim).filter(
                usuGim.id_UsuGim == idUsuGim
            ))
            usu = Usuario.query.get(idUsu)
            os.rmdir(f'Base/static/Imagenes/{(Gimnasio.query.get(idgim)).nombre_gimnasio.replace(" ","")}/{usu.nombre_usuario}_{usu.apellido_usuario}')
        con.execute(update(Gimnasio).filter(Gimnasio.id_gimnasio.notin_(
            usuGim.query.with_entities(usuGim.id_gimnasio).group_by(usuGim.id_gimnasio)
            )).values(habilitado = False))
        con.commit()
