const title = document.getElementById('title');
const registrateButton = document.getElementById('registrate');
const iniciaSesionButton = document.getElementById('inicia-sesion');
const input_user = document.getElementById('user');
const apellidos = document.getElementById('apellidos');
const olvide = document.getElementById('olvide');
const curp = document.getElementById('curp');
const sexo = document.getElementById('sex');
const civil = document.getElementById('civil');
const estado = document.getElementById('estado');
const municipio = document.getElementById('municipio');
const calle = document.getElementById('calle');
const colonia = document.getElementById('colonia');
const container = document.getElementById ('container');



if (title.textContent === 'Registrate') {
    olvide.style.display = 'none';
}

let isLoginClicked = false;
let isRegisterClicked = true;

// Registrate, esconde el "olvide contraseña" y "nombre"
registrateButton.addEventListener('click', () => {
    if(isRegisterClicked) {
        // Perform register form submission
        console.log('register form submitted');
        isRegisterClicked = false;
    } else {
    title.textContent = 'Registrate';
    registrateButton.style.backgroundColor = '#003053';
    registrateButton.style.color = '#fff';
    iniciaSesionButton.style.backgroundColor = '#0000004b';
    iniciaSesionButton.style.color = '#0000004b';
    input_user.style.display = 'flex';
    apellidos.style.display = 'flex';
    curp.style.display = 'flex';
    civil.style.display = 'flex';
    olvide.style.display = 'none';
    sexo.style.display = 'flex';
    estado.style.display = 'flex';
    municipio.style.display = 'flex';
    colonia.style.display = 'flex';
    calle.style.display = 'flex';
    container.style.height =  '1500px';
    isLoginClicked = false;
    isRegisterClicked = true;}
});


// boton inicia sesion, esconde el usuario y muestra "olvide contraseña"
iniciaSesionButton.addEventListener('click', () => {
    if (isLoginClicked) {
        // Perform login form submission
        console.log('Login form submitted');
        isLoginClicked = false;
    } else {
        title.textContent = 'Inicia Sesion';
        iniciaSesionButton.style.backgroundColor = '#003053';
        iniciaSesionButton.style.color = '#fff';
        registrateButton.style.backgroundColor = '#0000004b';
        registrateButton.style.color = '#0000004b';
        input_user.style.display = 'none';
        apellidos.style.display = 'none';
        olvide.style.display = 'flex';
        curp.style.display = 'none';
        civil.style.display = 'none';
        sexo.style.display = 'none';
        estado.style.display = 'none';
        municipio.style.display = 'none';
        colonia.style.display ='none';
        calle.style.display = 'none';
        container.style.height =  '535px';
        isLoginClicked = true;
        isRegisterClicked = false;
    }
});
