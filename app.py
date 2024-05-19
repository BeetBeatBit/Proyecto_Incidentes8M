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
app.secret_key = 'fj29P$#2@jT!QaL5'

#Conexion BD Yahir
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'aries1901'
app.config['MYSQL_DB'] = 'universidad'

#Configuracion para la conexion a la BD
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'coloso123'
#app.config['MYSQL_DB'] = 'universidad'


#Configuracion para la conexion a la BD (ANDREW)
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = '5248'
#app.config['MYSQL_DB'] = 'universidad'
#app.config['MYSQL_PORT'] = 3307  # Specify the port number


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

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        # Collect all form data
        matricula = request.form['matricula']
        ape_pat = request.form['ape_pat']
        ape_mat = request.form['ape_mat']
        nombres = request.form['nombres']
        curp = request.form['curp']
        genero = request.form['genero']
        est_civil = request.form['est_civil']
        estado = request.form['estado']
        municipio = request.form['municipio']
        colonia = request.form['colonia']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        celular = request.form['celular']
        email = request.form['email']
        fec_nacimiento = request.form['fec_nacimiento']
        nombre_dependencia = request.form['dependencia']  # Assume dependencia is the name passed from the form
        nombre_carrera = request.form['carrera']          # Assume carrera is the name passed from the form

        # Fetch cve_dependencia from the database
        cursor.execute("SELECT cve_dependencia FROM uni_dependencias WHERE nombre_dependencia = %s", (nombre_dependencia,))
        cve_dependencia_result = cursor.fetchone()
        cve_dependencia = cve_dependencia_result[0] if cve_dependencia_result else None

        # Fetch cve_carrera from the database
        cursor.execute("SELECT cve_carrera FROM uni_carreras WHERE nombre_carrera = %s", (nombre_carrera,))
        cve_carrera_result = cursor.fetchone()
        cve_carrera = cve_carrera_result[0] if cve_carrera_result else None

        # Check if both cve_dependencia and cve_carrera are found
        if not cve_dependencia or not cve_carrera:
            return "Dependencia or Carrera not found", 400  # Return an error if any ID is not found

        # Insert data into database
        insert_query = """
        INSERT INTO uni_alumnos (matricula, ape_pat, ape_mat, nombres, curp, genero, est_civil, estado, municipio, colonia, direccion, telefono, celular, email, fec_nacimiento, cve_dependencia, cve_carrera)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (matricula, ape_pat, ape_mat, nombres, curp, genero, est_civil, estado, municipio, colonia, direccion, telefono, celular, email, fec_nacimiento, cve_dependencia, cve_carrera))
        mysql.connection.commit()
        return 'Registro completado'  # Or redirect to another page

    # For GET request, fetch dependencias and carreras
    cursor.execute("SELECT nombre_dependencia, cve_dependencia FROM uni_dependencias")
    dependencias = cursor.fetchall()
    cursor.execute("SELECT nombre_carrera, cve_carrera FROM uni_carreras")
    carreras = cursor.fetchall()
    return render_template('registro.html', dependencias=dependencias, carreras=carreras)


    

#Conexion de base de datos
@app.route('/login', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contrasena = request.form.get('contraseña')

        if not correo or not contrasena:
            return render_template('/login.html', error='Por favor, completa todos los campos requeridos.')

        if mysql.connection is None:
            return render_template('/login.html', mensaje='Error al conectarse a la base de datos')

        try:
            mycursor = mysql.connection.cursor()
            mycursor.execute("SELECT id, correo, contraseña, tipo_usuario FROM admin_users WHERE correo = %s", (correo,))
            result = mycursor.fetchone()

            if result:
                idUsuario, emailUsuario, contrasena_bd, tipo_usuario = result
                
                if contrasena == contrasena_bd:
                    session['correo'] = correo
                    session['idUsuario'] = idUsuario
                    session['tipo_usuario'] = tipo_usuario  # Asegurarse de que 'tipo_usuario' se guarda en la base de datos

                    # Autenticacion en dos pasos
                    codigo2FA = generar_codigo_autenticacion()
                    fechaActual = obtenerFechaActual()

                    enviar_correo_autenticacion(codigo2FA, emailUsuario)
                    guardar_codigo_autenticacion_bd(codigo2FA, idUsuario, fechaActual)

                    session['fechaActual'] = fechaActual

                    return redirect(url_for('verificar_codigo'))
                else:
                    return render_template('/login.html', error='Contraseña incorrecta')
            else:
                return render_template('/login.html', error='No se encontró el usuario')
        except MySQLdb._exceptions.MySQLError as error:
            print("Error al ejecutar la consulta a la base de datos: {}".format(error))
            return render_template('/login.html', error='Error al ejecutar la consulta a la base de datos')
    else:
        return render_template('/login.html')



@app.route('/logout')
def logout():
    session.pop('correo', None) #Eliminar la variable de sesión username
    return render_template ('/login.html')

#Verificacion en dos pasos
@app.route('/verificar_codigo', methods=['GET', 'POST'])
def verificar_codigo():
    if request.method == 'POST':
        codigoUsuario = request.form.get('codigo_verificacion')
        tipo_usuario = session.get('tipo_usuario')  # Asegúrate de que esto es correcto y consistente

        if tipo_usuario == 'admin':
            usuarioId = session.get('idUsuario')
        elif tipo_usuario == 'profesor':
            usuarioId = session.get('cve_profesor')
        else:
            return render_template('verificacion.html', error='Tipo de usuario no reconocido.')


        cursor = mysql.connection.cursor()
        # Asegúrate de que la consulta está utilizando el ID de usuario correcto y ordenando por fecha descendente
        cursor.execute("SELECT code FROM twofactorcodes WHERE idUsuario = %s ORDER BY fecha DESC LIMIT 1", (usuarioId,))
        result = cursor.fetchone()

        if result:
            codigo_db = result[0]
            if codigoUsuario == codigo_db:
                if tipo_usuario == 'admin':
                #if session.get('tipo_usuario') == 'admin':
                    return redirect(url_for('dashboard'))  # Redirección al dashboard de administradores
                elif tipo_usuario == 'profesor':
                #elif session.get('tipo_usuario') == 'profesor':
                    return redirect(url_for('profesor_dashboard'))  # Redirección al dashboard de profesores
                else:
                    return render_template('verificacion.html', error='Tipo de usuario no reconocido.')


    return render_template('verificacion.html')



#FUNCION PARA GENERAR CODIGO DE AUTENTIFICACION
def generar_codigo_autenticacion():
    codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return codigo

def enviar_correo_autenticacion(codigoAutenticacion, emailUsuario):
    try:
        mensaje = MIMEMultipart()
        mensaje['From'] = 'llnbllzero@gmail.com'
        mensaje['To'] = emailUsuario
        mensaje['Subject'] = 'Codigo de Verificacion'
        texto = f'Este es tu codigo de verificacion para accesar: \n {codigoAutenticacion} \n\n'
        mensaje.attach(MIMEText(texto))
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login('clinica.lolsito@gmail.com', 'roqjmysztulyuiqf')
        servidor.sendmail('llnbllzero@gmail.com', emailUsuario, mensaje.as_string())
        servidor.quit()
        print("Correo enviado con código:", codigoAutenticacion)  # Para depuración
        return True
    except Exception as e:
        print(f"Ha ocurrido un error al enviar el correo: {str(e)}")
        return False


def guardar_codigo_autenticacion_bd(codigoAutenticacion, usuario_id, fechaActual):
    try:
        cursor = mysql.connection.cursor()
        insert_query = "INSERT INTO twofactorcodes (code, idUsuario, fecha) VALUES (%s, %s, %s)"
        data = (codigoAutenticacion, usuario_id, fechaActual)
        cursor.execute(insert_query, data)
        mysql.connection.commit()
        cursor.close()
        print("Código de autenticación guardado con éxito en la base de datos.")
    except MySQLdb._exceptions.MySQLError as err:
        print(f"Error al guardar el código de autenticación en la base de datos: {err}")

def handle_login_process(emailUsuario, usuario_id):
    # Generar el código de autenticación
    codigoAutenticacion = generar_codigo_autenticacion()
    print("Código generado y a enviar:", codigoAutenticacion)  # Para depuración

    # Enviar el correo con el código
    if enviar_correo_autenticacion(codigoAutenticacion, emailUsuario):
        # Obtener la fecha actual
        fechaActual = obtenerFechaActual()
        # Guardar el código en la base de datos
        guardar_codigo_autenticacion_bd(codigoAutenticacion, usuario_id, fechaActual)
        return True
    else:
        print("Error al enviar el correo")
        return False




#FUNCION PARA OBTENER LA FECHA PARA LA AUTENTIFICACION DE 2 PASOS TENGA UN TIEMPO LIMITE
def obtenerFechaActual():

    # Obtiene la fecha y hora actual
    fecha_hora_actual = datetime.datetime.now()

    # Formatea la fecha y hora en el formato deseado (YYYY-MM-DD HH:MM:SS)
    fecha_hora_formateada = fecha_hora_actual.strftime('%Y-%m-%d %H:%M:%S')

    return fecha_hora_formateada



# FUNCIONES PARA RELLENAR EL DASHBOARD DE ALUMNOS
@app.route('/login_alumno', methods=['GET', 'POST'])
def login_alumno():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        # Aquí añadirías la lógica para verificar las credenciales del profesor.
        return redirect(url_for('alumno_dashboard'))
    return render_template('login_alumno.html')

    

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

# Ruta para el panel de control de profesores 
@app.route('/profesor_dashboard')
def profesor_dashboard():
    # Verificar si la sesión del profesor está activa
    if 'cve_profesor' not in session:
        return redirect(url_for('login'))

    # Obtener la clave del profesor desde la sesión
    cve_profesor = session['cve_profesor']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM uni_profesor WHERE cve_profesor = %s", (cve_profesor,))
    profesor = cursor.fetchone()
    cursor.close()

    if not profesor:
        return "No tienes permiso para acceder a este panel."

    # Renderizar el dashboard de profesores
    return render_template('profesor_dashboard.html')


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
@app.route('/login_profesor', methods=['GET', 'POST'])
def login_profesor():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contrasena = request.form.get('password')

        if not correo or not contrasena:
            return render_template('login_profesor.html', error='Por favor, completa todos los campos.')

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT cve_profesor, email, contraseña FROM uni_profesor WHERE email = %s", (correo,))
            profesor = cursor.fetchone()

            if profesor and profesor[2] == contrasena:
                session['correo_profesor'] = correo  # Guardar el correo en la sesión
                session['cve_profesor'] = profesor[0]
                session['tipo_usuario'] = 'profesor'

                # Generación y envío del código de verificación en dos pasos
                handle_login_process(profesor[1], profesor[0])

                return redirect(url_for('verificar_codigo'))
            else:
                return render_template('login_profesor.html', error='Correo o contraseña incorrectos.')

        except MySQLdb._exceptions.MySQLError as error:
            return render_template('login_profesor.html', error=f'Error al consultar la base de datos: {str(error)}')

    return render_template('login_profesor.html')







if __name__ == '__main__':
    app.run(debug=True)