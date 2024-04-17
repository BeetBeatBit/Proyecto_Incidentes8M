import random
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import smtplib
import datetime
import mysql.connector
import MySQLdb._exceptions
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'vulnerabilidades'

#Configuracion para la conexion a la BD
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'coloso123'
app.config['MYSQL_DB'] = 'universidad'

# try:
#     mydb = mysql.connector.connect(
#         host = "localhost",
#         port = "3306",
#         user= "root",
#         password = "coloso123",
#         database = "universidad"
#     )

#     print("Conexión exitosa a la base de datos. \n")

# except mysql.connector.Error as error:
#     print("Error al conectarse a la base de datos: {}".format(error))
#     mydb = None

mysql = MySQL(app)

@app.route('/')
def login():
    return render_template('login.html')

# RUTAS PARA LOS TEMPLATES
@app.route("/")
def alumnos():
    return render_template("alumnos.html")

@app.route("/verificacion")
def verificacion():
    return render_template("verificacion.html")


#Conexion de base de datos
@app.route('/login', methods = ['GET','POST'])
def login2():
    if mysql.connection is None:
        return render_template('/login.html', mensaje='Error al conectarse a la base de datos')
    
    correo = request.form['correo']
    contrasena = request.form['contraseña']

    try:
        mycursor = mysql.connection.cursor()

        mycursor.execute("SELECT id, correo, contraseña FROM admin_users WHERE correo = %s", (correo,))
        result = mycursor.fetchone()

        if result:
            idUsuario, emailUsuario, contrasena_bd = result
            
            if contrasena == contrasena_bd:
                session['correo'] = correo  # Almacenar el nombre de usuario en la sesión

                #Autenticacion en dos pasos
                codigo2FA = generar_codigo_autenticacion()
                fechaActual = obtenerFechaActual()

                enviar_correo_autenticacion(codigo2FA, emailUsuario)
                guardar_codigo_autenticacion_bd(codigo2FA, idUsuario, fechaActual)

                # Almacena las variables en la sesión
                session['idUsuario'] = idUsuario
                session['fechaActual'] = fechaActual

                return render_template('/verificacion.html', correcta='Has iniciado sesión correctamente')
            else:
                # Nombre de usuario o contraseña incorrectos
                return render_template('/login.html', error='Nombre de usuario o contraseña incorrectos')
        else:
            # Nombre de usuario no encontrado en la base de datos
            return render_template('/login.html', error='Nombre de usuario o contraseña incorrectos')
    except MySQLdb._exceptions.MySQLError as error:
        print("Error al ejecutar la consulta a la base de datos: {}".format(error))
        return render_template('/login.html', error='Error al ejecutar la consulta a la base de datos')

@app.route('/logout')
def logout():
    session.pop('correo', None) #Eliminar la variable de sesión username
    return render_template ('/login.html')

#Verificacion en dos pasos
@app.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    codigoUsuario = None

    if request.method == 'POST':

        try:
            codigoUsuario = request.form['codigo_verificacion']
            idUsuarioVer = session.get('idUsuario')
            fechaActualVer = session.get('fechaActual')

            print(idUsuarioVer)
            print(fechaActualVer)

            cursor = mysql.connection.cursor()

            # Seleccionar los datos en la tabla twofactorcodes
            select_query = "SELECT code FROM twofactorcodes WHERE idUsuario = %s AND fecha = %s"
            data = (idUsuarioVer, fechaActualVer)
            cursor.execute(select_query, data)

            # Recuperar el resultado de la consulta
            result = cursor.fetchone()
            cursor.close()

            if result:
                
                if (codigoUsuario == result[0]):
                    estado = 'VERIFICACION COMPLETADA'
                    return render_template('dashboard.html', estado=estado)
                else:
                    estado = 'CODIGO INCORRECTO'
                    return render_template('verificacion.html', estado=estado)

            else:
                estado = 'Error al verificar el código'
                return render_template('verificacion.html', estado=estado)

            

        except mysql.connector.Error as err:
            estado = 'Error al verificar el código'
            print(f"Error al consultar la base de datos: {err}")
            return render_template('verificacion.html', estado=estado)

#FUNCION PARA GENERAR CODIGO DE AUTENTIFICACION
def generar_codigo_autenticacion():
    codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return codigo

def enviar_correo_autenticacion(codigoAutenticacion, emailUsuario):

    try:
        # Construir el mensaje de correo electrónico
        mensaje = MIMEMultipart()
        mensaje['From'] = 'llnbllzero@gmail.com'
        mensaje['To'] = emailUsuario
        mensaje['Subject'] = 'Codigo de Verificacion'


        texto = f'Este es tu codigo de verificacion para accesar: \n {codigoAutenticacion} \n\n'
        mensaje.attach(MIMEText(texto))

        # Enviar el mensaje de correo electrónico
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login('clinica.lolsito@gmail.com', 'roqjmysztulyuiqf')
        servidor.sendmail('llnbllzero@gmail.com', emailUsuario, mensaje.as_string())
        servidor.quit()

        return True
    
    except Exception as e:
        print(f"Ha ocurrido un error: {str(e)}")
        return False  # Retorna False en caso de error
    
#FUNCION PARA GUARDAR EL CODIGO EN LA BASE DE DATOS Y PODER INICIAR SESION
def guardar_codigo_autenticacion_bd(codigoAutenticacion, usuario_id, fechaActual):

    try:
        cursor = mysql.connection.cursor()

        # Insertar los datos en la tabla twofactorcodes
        insert_query = "INSERT INTO twofactorcodes (code, idUsuario, fecha) VALUES (%s, %s, %s)"
        data = (codigoAutenticacion, usuario_id, fechaActual)
        cursor.execute(insert_query, data)

        # Confirmar la transacción y cerrar la conexión
        mysql.connection.commit()
        cursor.close()
        #db.database.close()

        print("Código de autenticación guardado con éxito en la base de datos.")
    except MySQLdb._exceptions.MySQLError as err:
        print(f"Error al guardar el código de autenticación en la base de datos: {err}")



#FUNCION PARA OBTENER LA FECHA PARA LA AUTENTIFICACION DE 2 PASOS TENGA UN TIEMPO LIMITE
def obtenerFechaActual():

    # Obtiene la fecha y hora actual
    fecha_hora_actual = datetime.datetime.now()

    # Formatea la fecha y hora en el formato deseado (YYYY-MM-DD HH:MM:SS)
    fecha_hora_formateada = fecha_hora_actual.strftime('%Y-%m-%d %H:%M:%S')

    return fecha_hora_formateada

obtenerFechaActual()











# FUNCIONES PARA RELLENAR EL DASHBOARD DE ALUMNOS
@app.route('/alumnos.html', methods=['POST'])
def search():
    query = request.form['query']

    cursor = mysql.database.cursor()
    sql = "SELECT * FROM alumnos WHERE nombre LIKE %s OR apellido LIKE %s OR id LIKE %s"
    data = (f'%{query}%', f'%{query}%', f'%{query}%') 
    cursor.execute(sql, data)
    alumnos = cursor.fetchall()

    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in alumnos:
        insertObject.append(dict(zip(columnNames, record)))
    cursor.close()

    cursor.close()

    return render_template('alumnos.html', alumnos=insertObject)


# @app.route('/login', methods=['POST'])
# def login_post():
#     correo = request.form['correo']
#     contraseña = request.form['contraseña']

#     #verificar si el usuario es un administrador
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM admin_users WHERE correo = %s", (correo,))
#     admin_user = cur.fetchone()
#     cur.close()

#     print("admin_user:", admin_user)

#     if admin_user and admin_user[4] == contraseña:
#         session['user_id'] = admin_user[0] #guardar el id del administrador
#         return redirect(url_for('dashboard'))
#     else:
#         return redirect(url_for('login'))
    

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admin_users WHERE id = %s", (user_id,))
    admin = cur.fetchone()
    cur.close()

    if not admin:
        return "No tienes permiso"
    return render_template('dashboard.html')

# Ruta para el panel de control de alumnos
@app.route('/alumno_dashboard')
def alumno_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM uni_alumnos WHERE id = %s", (user_id,))
    alumno = cur.fetchone()
    cur.close()
    
    if not alumno:
        return "No tienes permiso para acceder a este panel."
    
    return render_template('alumno_dashboard.html')


# Ruta para el panel de control de profesores
@app.route('/profesor_dashboard')
def profesor_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM uni_profesor WHERE id = %s", (user_id,))
    profesor = cur.fetchone()
    cur.close()
    
    if not profesor:
        return "No tienes permiso para acceder a este panel."
    
    return render_template('profesor_dashboard.html')



if __name__ == '__main__':
    app.run(debug=True)