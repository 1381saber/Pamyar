// darkmode.js

document.addEventListener('DOMContentLoaded', () => {

    const themeSwitcherBtn = document.getElementById('theme-switcher-btn');
    const sunIconPath = "/pamyar_frontend/assets/sun-icon.svg";
    const moonIconPath = "/pamyar_frontend/assets/moon-icon.svg";

    /**
     * تم ذخیره شده را روی تگ <html> اعمال می‌کند.
     * @param {string} theme 
     */
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);

        if (themeSwitcherBtn) {
            const icon = themeSwitcherBtn.querySelector('img');
            if (theme === 'dark') {
                icon.src = sunIconPath;
                icon.alt = "تم روشن";
            } else {
                icon.src = moonIconPath;
                icon.alt = "تم تیره";
            }
        }
    };

    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    if (themeSwitcherBtn) {
        themeSwitcherBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';

            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
    }
});