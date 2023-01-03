from database import db

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key = True)
    nombre_usuario = db.Column(db.String(200))
    apellido_usuario = db.Column(db.String(200))
    documento_usuario = db.Column(db.Integer)
    contraseña_usuario = db.Column(db.String(200))
    cabeza_de_grupo = db.Column(db.Boolean)
    id_cabeza = db.Column(db.Integer)
    cargo_usuario = db.Column(db.String(30))
    email_usuario = db.Column(db.String(100))
    categoria = db.Column(db.String(20), nullable= True)

    def __str__(self):
        return f'''
        id: {self.id_usuario}
        nombre: {self.nombre_usuario}
        apelido: {self.apellido_usuario}
        cargo: {self.cargo_usuario}
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

    def __str__(self):
        return f'''
        id_gimnasio: {self.id_gimnasio}
        nombre: {self.nombre_gimnasio}
        direccion: {self.direccion_gimnasio}
        horarios: {self.horarios_gimnasio}
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
    fecha_Exa_Desa = db.Column(db.Date)
    fecha_Fetra = db.Column(db.Date)
    fecha_Enat = db.Column(db.Date)
    fecha_Aatee = db.Column(db.Date)
    id_UsuGim = db.Column(db.Integer, db.ForeignKey('usugim.id_UsuGim'))

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
    descripcion = db.Column(db.String(100))

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