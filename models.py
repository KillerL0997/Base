from database import db
import shutil

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key = True)
    nombre_usuario = db.Column(db.String(200), nullable= True)
    apellido_usuario = db.Column(db.String(200), nullable= True)
    documento_usuario = db.Column(db.Integer)
    contraseña_usuario = db.Column(db.String(200))
    id_cabeza = db.Column(db.Integer)
    cargo_usuario = db.Column(db.String(30))
    email_usuario = db.Column(db.String(100))
    categoria = db.Column(db.String(20), nullable= True)
    instructor = db.Column(db.Integer)

    def ordenarDatos(self,idCabeza,idInstructor, contra):
        self.nombre_usuario = self.nombre_usuario.capitalize()
        self.apellido_usuario = self.apellido_usuario.capitalize()
        self.id_cabeza = idCabeza
        self.instructor = idInstructor
        if contra:
            self.contraseña_usuario = contra

    def __str__(self):
        return f'''
        id: {self.id_usuario}
        nombre: {self.nombre_usuario}
        apelido: {self.apellido_usuario}
        documento: {self.documento_usuario}
        id cabeza: {self.id_cabeza}
        cargo: {self.cargo_usuario}
        mail: {self.email_usuario}
        categoria: {self.categoria}
        instructor: {self.instructor}
        '''


class Gimnasio(db.Model):
    __tablename__= 'gimnasio'
    id_gimnasio = db.Column(db.Integer, primary_key = True)
    nombre_gimnasio = db.Column(db.String(255), nullable= True)
    direccion_gimnasio = db.Column(db.String(255), nullable= True)
    habilitado = db.Column(db.Boolean)
    ubicacion_gimnasio = db.Column(db.String(500))
    instagram_gimnasio = db.Column(db.String(500))
    whats_gimnasio = db.Column(db.String(500))
    face_gimnasio = db.Column(db.String(500))
    logo_gimnasio = db.Column(db.String(500))

    def armarGim(self,dirLogo):
        self.capitalizarGim()
        self.habilitado = True
        self.logo_gimnasio = dirLogo

    def capitalizarGim(self):
        self.nombre_gimnasio = self.nombre_gimnasio.capitalize()
        self.direccion_gimnasio = self.direccion_gimnasio.capitalize()

    def __str__(self):
        return f'''
        id_gimnasio: {self.id_gimnasio}
        nombre: {self.nombre_gimnasio}
        direccion: {self.direccion_gimnasio}
        logo: {self.logo_gimnasio}
        '''

class horarioGim(db.Model):
    __tablename__= 'horariogim'
    idHorario = db.Column(db.Integer, primary_key = True)
    descripcion = db.Column(db.String(250))
    id_UsuGim = db.Column(db.Integer, db.ForeignKey('usugim.id_UsuGim'))

class Alumno(db.Model):
    __tablename__ = 'alumno'
    id_alumno = db.Column(db.Integer, primary_key = True)
    nombre_alumno = db.Column(db.String(200), nullable= True)  
    apellido_alumno = db.Column(db.String(200), nullable= True)   
    nacionalidad_alumno = db.Column(db.String(200), nullable= True)   
    documento_alumno = db.Column(db.Integer, nullable= True) 
    telefono_alumno = db.Column(db.Integer)   
    graduacion_alumno = db.Column(db.String(50), nullable= True)  
    fecha_inscripcion_alumno = db.Column(db.Date, nullable= True)
    observaciones_alumno = db.Column(db.Text)
    email_alumno = db.Column(db.String(100))
    localidad_alumno = db.Column(db.String(200), nullable= True)
    fecha_nacimiento_alumno = db.Column(db.Date, nullable= True)
    habilitado = db.Column(db.Boolean)
    fecha_Desa = db.Column(db.Date)
    id_UsuGim = db.Column(db.Integer, db.ForeignKey('usugim.id_UsuGim'))
    libreta = db.Column(db.String(20))
    foto = db.Column(db.String(500))

    def armarAlumno(self, fecha, idUsuGim, dirFoto):
        self.aluNomApe()
        self.habilitado = True
        self.fecha_inscripcion_alumno = fecha
        self.id_UsuGim = idUsuGim
        self.foto = dirFoto

    def aluNomApe(self):
        self.nombre_alumno = self.nombre_alumno.capitalize()
        self.apellido_alumno = self.apellido_alumno.capitalize()
    
    def cambiarFoto(self, dirDesa):
        self.foto = self.foto.replace('%C3%B3', 'ó')
        dirNueva = dirDesa + self.foto[self.foto.rfind("/"):]
        shutil.move(self.foto[1:], dirNueva)
        self.foto = dirNueva if dirNueva[0] == "/" else "/" + dirNueva

    def __str__(self):
        return f'''
        id_alumno: {self.id_alumno}
        nombre_alumno: {self.nombre_alumno}
        apellido_alumno: {self.apellido_alumno}  
        graduacion_alumno: {self.graduacion_alumno}
        '''

class aluEven(db.Model):
    __tablename__ = 'alueven'
    id_aluEven = db.Column(db.Integer, primary_key = True)
    id_alumno = db.Column(db.Integer, db.ForeignKey('alumno.id_alumno'))
    id_evento = db.Column(db.Integer, db.ForeignKey('eventos.id_evento'))

class Eventos(db.Model):
    __tablename__ = 'eventos'
    id_evento = db.Column(db.Integer, primary_key = True)
    fecha_evento = db.Column(db.Date, nullable= True)
    tipo_de_evento = db.Column(db.String(50), nullable= True)
    lugar_evento = db.Column(db.String(100))
    lugarOpc = db.Column(db.String(100))
    tipoOpc = db.Column(db.String(100))
    actRealizada = db.Column(db.Text)

    def __str__(self):
        return f'''
        id_evento: {self.id_evento}
        fecha_evento: {self.fecha_evento}
        tipo de evento: {self.tipo_de_evento}
        '''

class usuGim(db.Model):
    __tablename__ = 'usugim'
    id_UsuGim = db.Column(db.Integer, primary_key = True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    id_gimnasio = db.Column(db.Integer, db.ForeignKey('gimnasio.id_gimnasio'))
    id_cabeza = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

class usuNoti(db.Model):
    __tablename__ = 'usunoti'
    id_usuNoti = db.Column(db.Integer, primary_key = True)
    id_Usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    id_Notificacion = db.Column(db.Integer, db.ForeignKey('notificaciones.id_notificacion'))

class Notificaciones(db.Model):
    __tablename__ = 'notificaciones'
    id_notificacion = db.Column(db.Integer, primary_key = True)
    notificacion = db.Column(db.Text, nullable= True)
    asunto = db.Column(db.String(30), nullable= True)

class Matriculas(db.Model):
    __tablename__ = 'matriculas'
    id_matricula = db.Column(db.Integer, primary_key = True)
    id_Alumno = db.Column(db.Integer, db.ForeignKey('alumno.id_alumno'))
    tipo = db.Column(db.String(30), nullable = True)
    fecha = db.Column(db.Date, nullable = True)

class Imagen(db.Model):
    __tablename__ = 'imagenes'
    id_imagen = db.Column(db.Integer, primary_key = True)
    id_evento = db.Column(db.Integer, db.ForeignKey('eventos.id_evento'))
    direccion = db.Column(db.String(500))
    tipo_imagen = db.Column(db.String(50))