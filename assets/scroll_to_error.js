document.addEventListener('DOMContentLoaded', function () {
    // Función para manejar el desplazamiento cuando la página carga o cuando el hash cambia
    function handleScroll() {
        if (window.location.hash === '#error') {
            const element = document.getElementById('sens-error-message');
            if (element) {
                element.scrollIntoView({behavior: 'smooth'});
            }
        }
    }

    // Escuchar cambios de hash
    window.addEventListener('hashchange', handleScroll);

    // Llamar al cargar la página por si el hash ya está seteado
    handleScroll();
});
