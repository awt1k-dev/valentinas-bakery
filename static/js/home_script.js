// Устанавливаем текущий год в футере
document.getElementById('year').textContent = new Date().getFullYear();

// Простая анимация навигации при скролле
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
});

// УПРОЩЕННАЯ АНИМАЦИЯ ПОЯВЛЕНИЯ ЭЛЕМЕНТОВ
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            
            if (entry.target.classList.contains('contact-item')) {
                entry.target.style.transform = 'translateX(0)';
            } else {
                entry.target.style.transform = 'translateY(0)';
            }
            
            // Убираем наблюдение после появления
            observer.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
});

// Наблюдаем за элементами
document.querySelectorAll('.product-card, .contact-item, .section-title').forEach(el => {
    // Начальные стили заданы в CSS (opacity: 0 и transform) или скрипте
    if (el.classList.contains('product-card')) {
        el.style.transform = 'translateY(30px)';
    }
    if (el.classList.contains('contact-item')) {
        el.style.transform = 'translateX(-20px)';
    }
    if (el.classList.contains('section-title')) {
        el.style.transform = 'translateY(20px)';
    }
    // ВАЖНО: transition добавлен здесь или в CSS, чтобы анимация работала
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    
    observer.observe(el);
});

// Плавная прокрутка для якорных ссылок
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 100,
                behavior: 'smooth'
            });
        }
    });
});

// Индикатор прогресса скролла
const progressBar = document.createElement('div');
progressBar.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 0%;
    height: 3px;
    background: linear-gradient(45deg, var(--accent), var(--accent-dark));
    z-index: 9999;
    transition: width 0.1s ease;
`;
document.body.appendChild(progressBar);

window.addEventListener('scroll', () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    progressBar.style.width = scrolled + '%';
});

// Убираем прелоадер после загрузки
window.addEventListener('load', () => {
    const preloader = document.querySelector('.preloader');
    if (preloader) {
        setTimeout(() => {
            preloader.style.opacity = '0';
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 300);
        }, 300);
    }
    
    // Принудительно показываем элементы, если они уже в видимой зоне (страховка)
    document.querySelectorAll('.product-card, .contact-item, .section-title').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            el.style.opacity = '1';
            el.style.transform = 'translate(0)';
        }
    });
});

// Анимация при наведении на кнопки
document.querySelectorAll('.cta-button').forEach(button => {
    button.addEventListener('mouseenter', () => {
        button.style.transform = 'translateY(-3px)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.transform = 'translateY(0)';
    });
});