from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired
from wtforms import StringField, IntegerField, DateField, EmailField, SelectField, TextAreaField, PasswordField, BooleanField, SubmitField
from datetime import datetime

class UsuarioForm(FlaskForm):
    nombre_usuario = StringField("nombre_usuario", validators=[DataRequired()])
    apellido_usuario = StringField("apellido_usuario", validators=[DataRequired()])
    documento_usuario = IntegerField("documento_usuario", validators=[DataRequired()])
    contraseña_usuario = PasswordField("contraseña_usuario")
    id_cabeza = IntegerField("id_cabeza")
    cargo_usuario = SelectField("cargo_usuario", validators=[DataRequired()], choices = [('Usuario', 'Usuario'),('Administrador','Administrador'),('Cabeza','Cabeza')])
    email_usuario = EmailField("email_usuario", validators=[DataRequired()])
    categoria = SelectField("categoria", validators=[DataRequired()], choices = [('I Dan','I Dan'),('II Dan','II Dan'),('III Dan','III Dan'),('IV Dan','IV Dan'),('V Dan','V Dan'),('VI Dan','VI Dan'),('VII Dan','VII Dan'),('VIII Dan','VIII Dan'),('IX Dan','IX Dan')]) 

class GimnasioForm(FlaskForm):
    nombre_gimnasio = StringField("nombre_gimnasio", validators=[DataRequired()])
    direccion_gimnasio = StringField("direccion_gimnasio", validators=[DataRequired()])
    ubicacion_gimnasio = StringField("ubicacion_gimnasio")
    instagram_gimnasio = StringField("instagram_gimnasio")
    whats_gimnasio = StringField("whats_gimnasio")
    face_gimnasio = StringField("face_gimnasio")

class AlumnoForm(FlaskForm):
    nombre_alumno = StringField("nombre_alumno", validators=[DataRequired()])
    apellido_alumno = StringField("apellido_alumno", validators=[DataRequired()])
    nacionalidad_alumno = StringField("nacionalidad_alumno", validators=[DataRequired()])
    documento_alumno = IntegerField("documento_alumno", validators=[DataRequired()])
    telefono_alumno = IntegerField("telefono_alumno")  
    graduacion_alumno = SelectField("graduacion_alumno", validators=[DataRequired()], choices = [('Blanco','Blanco'),('Blanco Pta. Amarilla','Blanco Pta. Amarilla'),('Amarillo','Amarillo'),('Amarillo Pta. Verde','Amarillo Pta. Verde'),('Verde','Verde'),('Verde Pta. Azul','Verde Pta. Azul'),('Azul','Azul'),('Azul Pta. Roja','Azul Pta. Roja'),('Rojo','Rojo'),('Rojo Pta. Negra','Rojo Pta. Negra'),('I Dan','I Dan'),('II Dan','II Dan'),('III Dan','III Dan'),('IV Dan','IV Dan'),('V Dan','V Dan'),('VI Dan','VI Dan'),('VII Dan','VII Dan')]) 
    fecha_inscripcion_alumno = DateField("fecha_inscripcion_alumno", default= datetime.utcnow())
    observaciones_alumno = TextAreaField("observaciones_alumno")
    email_alumno = EmailField("email_alumno")
    localidad_alumno = StringField("localidad_alumno", validators=[DataRequired()])
    fecha_nacimiento_alumno = DateField("fecha_nacimiento_alumno", validators=[DataRequired()], default= datetime.utcnow())

class ExamenForm(FlaskForm):
    fecha_evento = DateField("fecha_examen", validators= [DataRequired()])
    tipo_de_evento = SelectField("tipo_de_evento", validators= [DataRequired()], choices=(('Examen','Examen'),('Torneo','Torneo'),('Otros eventos','Otros eventos')))
    lugar_evento = StringField("lugar_evento")
    lugarOpc = StringField("lugarOpc")
    tipoOpc = StringField("tipoOpc")
    actRealizada = TextAreaField("actRealizada")

class NotificacionForm(FlaskForm):
    notificacion = TextAreaField("notificacion", validators= [DataRequired()])
    asunto = SelectField("asunto", validators=[DataRequired()], choices= [("Torneo","Torneo"),("Examen","Examen"),("Clase de danes","Clase de danes"),("Reunion","Reunión"),("Otros asuntos","Otros asuntos")]) 

class MatriculasForm(FlaskForm):
    tipo = StringField("tipo")
    fecha = DateField("fecha")

class Usuario_Gimnasio(FlaskForm):
    gimnasio = SelectField("gimnasio", choices=[])

class Gimnasio_Usuario(FlaskForm):
    usuario = SelectField("usuario", choices=[])

class DatoForm(FlaskForm):
    dato = SelectField("dato", choices=[])
