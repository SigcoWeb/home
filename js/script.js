// Inicializar EmailJS con las credenciales proporcionadas
(function() {
    emailjs.init("lpFEo4rg9tVJsaSbQ");
})();

// Carrusel functionality
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.carousel');
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    let currentIndex = 0;
    const totalSlides = slides.length;

    // Function to update carousel position
    function updateCarousel() {
        carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
        
        // Update dots
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });
    }

    // Next slide
    nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % totalSlides;
        updateCarousel();
    });

    // Previous slide
    prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + totalSlides) % totalSlides;
        updateCarousel();
    });

    // Dot navigation
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentIndex = index;
            updateCarousel();
        });
    });

    // Auto slide
    setInterval(() => {
        currentIndex = (currentIndex + 1) % totalSlides;
        updateCarousel();
    }, 6000);

    // Mobile menu toggle
    const mobileMenu = document.querySelector('.mobile-menu');
    const nav = document.querySelector('nav ul');
    
    mobileMenu.addEventListener('click', () => {
        nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
    });

    // Form submission with EmailJS
    const contactForm = document.getElementById('contactForm');
    const formMessage = document.getElementById('formMessage');
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitBtn = contactForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        // Show loading state
        submitBtn.textContent = 'Enviando...';
        submitBtn.disabled = true;
        
        // Send email using EmailJS con las credenciales actualizadas
        emailjs.sendForm('service_giq06ku', 'template_n27nn44', contactForm)
            .then(function(response) {
                console.log('SUCCESS!', response.status, response.text);
                formMessage.textContent = '¡Mensaje enviado con éxito! Nos pondremos en contacto pronto.';
                formMessage.className = 'form-message success';
                formMessage.style.display = 'block';
                contactForm.reset();
            }, function(error) {
                console.log('FAILED...', error);
                formMessage.textContent = 'Hubo un error al enviar el mensaje. Por favor, inténtelo de nuevo.';
                formMessage.className = 'form-message error';
                formMessage.style.display = 'block';
            })
            .finally(function() {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                
                // Hide message after 5 seconds
                setTimeout(() => {
                    formMessage.style.display = 'none';
                }, 5000);
            });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (window.innerWidth <= 768) {
                    nav.style.display = 'none';
                }
            }
        });
    });
});