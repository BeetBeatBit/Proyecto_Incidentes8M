from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
app = Flask(__name__)

#Configuracion para la conexion a la BD
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'aries1901'
app.config['MYSQL_DB'] = 'universidad'

mysql = MySQL(app)

@app.route('/')
def login():
    return render_template('login.html')

# RUTAS PARA LOS TEMPLATES
@app.route("/")
def alumnos():
    return render_template("alumnos.html")

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


@app.route('/login', methods=['POST'])
def login_post():
    correo = request.form['correo']
    contraseña = request.form['contraseña']

    #verificar si el usuario es un administrador
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM admin_users WHERE correo = %s", (correo,))
    admin_user = cur.fetchone()
    cur.close()

    print("admin_user:", admin_user)

    if admin_user and admin_user[4] == contraseña:
        session['user_id'] = admin_user[0] #guardar el id del administrador
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))
    

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
    app.secret_key = 'vulnerabilidades'
    app.run(debug=True)