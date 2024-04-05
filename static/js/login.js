const title = document.getElementById('title');
const registrateButton = document.getElementById('registrate');
const iniciaSesionButton = document.getElementById('inicia-sesion');
const input_user = document.getElementById('user');
const olvide = document.getElementById('olvide');


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
    registrateButton.style.backgroundColor = '#4c00b4';
    registrateButton.style.color = '#fff';
    iniciaSesionButton.style.backgroundColor = '#0000004b';
    iniciaSesionButton.style.color = '#0000004b';
    input_user.style.display = 'flex';
    olvide.style.display = 'none';
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
        iniciaSesionButton.style.backgroundColor = '#4c00b4';
        iniciaSesionButton.style.color = '#fff';
        registrateButton.style.backgroundColor = '#0000004b';
        registrateButton.style.color = '#0000004b';
        input_user.style.display = 'none';
        olvide.style.display = 'flex';
        isLoginClicked = true;
        isRegisterClicked = false;
    }
});
