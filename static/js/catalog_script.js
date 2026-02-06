document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Установка года
    const yearElement = document.getElementById("year");
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }

    // 2. Убираем прелоадер
    const preloader = document.querySelector('.preloader');
    if (preloader) {
        setTimeout(() => {
            preloader.style.opacity = '0';
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 300);
        }, 500);
    }

    // 3. Эффект скролла для навбара
    const nav = document.querySelector('.nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });

    // 4. Логика фильтрации с анимацией
    const filterButtons = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    // Показываем карточки с анимацией при загрузке
    productCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 50)); // Каскадная задержка
    });

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Удаляем класс active у всех кнопок
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Добавляем active нажатой кнопке
            button.classList.add('active');

            const filterValue = button.getAttribute('data-filter');

            productCards.forEach(card => {
                const category = card.getAttribute('data-category');

                if (filterValue === 'all' || category === filterValue) {
                    card.style.display = 'flex'; 
                    
                    // Сброс стилей для анимации
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.95)';
                    
                    // Небольшая задержка для запуска анимации CSS
                    setTimeout(() => {
                        card.style.transition = 'all 0.4s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'scale(1)';
                    }, 50);
                } else {
                    // Анимация исчезновения
                    card.style.opacity = '0';
                    card.style.transform = 'scale(0.9)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
});