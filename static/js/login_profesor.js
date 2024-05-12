
// Botón de inicio de sesión
const loginButton = document.getElementById('login-btn');

loginButton.addEventListener('click', () => {
    // Obtén los valores de los campos del formulario de inicio de sesión
    const correo = document.querySelector('input[type="email"]').value;
    const contraseña = document.querySelector('input[type="password"]').value;

    // Crea un objeto FormData para enviar los datos al servidor
    const formData = new FormData();
    formData.append('correo', correo);
    formData.append('contraseña', contraseña);

    // Envía una solicitud POST al servidor para iniciar sesión
    fetch('/login_profesor', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        // Maneja la respuesta del servidor
        if (response.ok) {
            // Si la respuesta es exitosa, redirige a la página de dashboard
            window.location.href = '/verificacion';
        } else {
            // Si la respuesta no es exitosa, muestra un mensaje de error al usuario
            console.error('Error al iniciar sesión');
            // Aquí puedes mostrar un mensaje de error en tu interfaz de usuario
        }
    })
    .catch(error => {
        console.error('Error al enviar la solicitud:', error);
    });
});