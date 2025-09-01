// plusscript.js (داخل DOMContentLoaded)
document.addEventListener('DOMContentLoaded', () => {

    const userEmailElement = document.querySelector('.user-email');
    const userNameElement = document.querySelector('.user-name');

    if (userEmailElement && userNameElement) {

        const fetchUserProfile = async() => {
            const authToken = localStorage.getItem('authToken');
            if (!authToken) {
                window.location.href = 'login.html';
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/profile/`, {
                    headers: { 'Authorization': `Token ${authToken}` }
                });

                if (response.ok) {
                    const data = await response.json();

                    userNameElement.textContent = "کاربر پمیار";
                    userEmailElement.textContent = data.email;

                    if (data.avatar_url) {
                        const uniqueUrl = `${data.avatar_url}?t=${new Date().getTime()}`;
                        localStorage.setItem('userAvatar', uniqueUrl);

                        loadUserAvatar();
                    }

                } else {
                    console.error("Failed to fetch user profile, redirecting to login.");
                    localStorage.removeItem('authToken');
                    window.location.href = 'login.html';
                }
            } catch (error) {
                console.error("Error fetching user profile:", error);
            }
        };

        fetchUserProfile();
    }

});