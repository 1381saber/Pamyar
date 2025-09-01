// main.js

const API_BASE_URL = 'http://127.0.0.1:8000/api';
const authToken = localStorage.getItem('authToken');

const fetchAndDisplayUserData = async() => {
    if (!authToken) {
        document.querySelectorAll('.profile-avatar, #avatar-preview-img').forEach(img => {
            img.src = 'assets/my-default-avatar.png';
        });
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/profile/`, {
            headers: { 'Authorization': `Token ${authToken}` }
        });

        if (response.ok) {
            const data = await response.json();

            const userEmailElement = document.querySelector('.user-email');
            if (userEmailElement && data.email) {
                userEmailElement.textContent = data.email;
            }

            if (data.avatar_url) {
                const uniqueUrl = `${data.avatar_url}?t=${new Date().getTime()}`;
                localStorage.setItem('userAvatar', uniqueUrl);
                document.querySelectorAll('.profile-avatar, #avatar-preview-img').forEach(img => {
                    img.src = uniqueUrl;
                });
            } else {
                localStorage.removeItem('userAvatar');
                document.querySelectorAll('.profile-avatar, #avatar-preview-img').forEach(img => {
                    img.src = 'assets/default_avatar.png';
                });
            }
        } else {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userAvatar');
        }
    } catch (error) {
        console.error("Error fetching user profile data:", error);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const cachedAvatar = localStorage.getItem('userAvatar');
    if (cachedAvatar) {
        document.querySelectorAll('.profile-avatar, #avatar-preview-img').forEach(img => {
            img.src = cachedAvatar;
        });
    }
    fetchAndDisplayUserData();
});