document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;
    const html = document.documentElement;
    const themeText = toggle.querySelector('.theme-text');
    const theme = localStorage.getItem('theme');

    if (theme === 'light') {
        html.setAttribute('data-theme', 'light');
        themeText.textContent = 'Светлая тема';
    } else {
        themeText.textContent = 'Тёмная тема';
    }

    toggle.addEventListener('click', (e) => {
        e.preventDefault();
        const isLight = html.getAttribute('data-theme') === 'light';
        if (isLight) {
            html.removeAttribute('data-theme');
            themeText.textContent = 'Тёмная тема';
            localStorage.setItem('theme', '');
        } else {
            html.setAttribute('data-theme', 'light');
            themeText.textContent = 'Светлая тема';
            localStorage.setItem('theme', 'light');
        }
        document.querySelector('.user_dropdown')?.classList.remove('open');
    });
});
