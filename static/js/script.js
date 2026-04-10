// Esperar a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Lógica para el año dinámico en el footer
    const footer_copy = document.getElementById("footer-copy");
    if (footer_copy) {
        const year = new Date().getFullYear(); 
        // Nota: He mantenido el texto exacto que me pediste "SaaS Control"
        // Si quieres que diga "CrediFlow", cámbialo aquí abajo.
        footer_copy.innerHTML = `&copy; ${year} SaaS Control. Todos los derechos reservados.`;
    }

    // 2. Lógica para el scroll suave (opcional pero mejora la experiencia)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Ajuste por la navbar fixed
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Función para el botón de precios (ejemplo)
function contactSales() {
    alert("¡Excelente! Estás a un paso de simplificar tu negocio. Te redirigiremos a la página de registro.");
    // window.location.href = "/registro/"; // Cambia esto por tu URL real de Django
}