document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    const icon = toggle.querySelector('.theme-icon');
    const theme = localStorage.getItem('theme');

    if (theme === 'light') {
        html.setAttribute('data-theme', 'light');
        icon.textContent = '☀️';
    } else {
        icon.textContent = '🌙';
    }

    toggle.addEventListener('click', () => {
        const isLight = html.getAttribute('data-theme') === 'light';
        if (isLight) {
            html.removeAttribute('data-theme');
            icon.textContent = '🌙';
            localStorage.setItem('theme', '');
        } else {
            html.setAttribute('data-theme', 'light');
            icon.textContent = '☀️';
            localStorage.setItem('theme', 'light');
        }
    });
});
