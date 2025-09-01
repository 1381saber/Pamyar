document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async() => {
            try {
                await fetch(`${API_BASE_URL}/logout/`, {
                    method: 'POST',
                    headers: { 'Authorization': `Token ${localStorage.getItem('authToken')}` }
                });
            } catch (error) {
                console.error("Logout request failed, but logging out from frontend anyway.", error);
            } finally {
                // **مهمترین بخش:** پاکسازی کامل localStorage
                localStorage.removeItem('authToken');
                localStorage.removeItem('userAvatar');
                alert("شما با موفقیت خارج شدید.");
                window.location.href = 'index.html';
            }
        });
    }
});