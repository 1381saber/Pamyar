document.addEventListener('DOMContentLoaded', () => {

    const avatarForm = document.getElementById('avatar-form');

    if (!avatarForm) {
        return;
    }

    const API_BASE_URL = 'http://127.0.0.1:8000/api';
    const avatarInput = document.getElementById('avatar-input');
    const avatarPreviewImg = document.getElementById('avatar-preview-img');
    let newAvatarFile = null;

    avatarInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {

            newAvatarFile = e.target.files[0];
            avatarPreviewImg.src = URL.createObjectURL(newAvatarFile);
        }
    });

    avatarForm.addEventListener('submit', async(e) => {
        e.preventDefault();

        if (!newAvatarFile) {
            alert("لطفاً یک عکس جدید انتخاب کنید.");
            return;
        }

        const formData = new FormData();
        formData.append('avatar', newAvatarFile);
        const authToken = localStorage.getItem('authToken');

        try {
            const response = await fetch(`${API_BASE_URL}/profile/change-avatar/`, {
                method: 'POST',
                headers: { 'Authorization': `Token ${authToken}` },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                alert(data.message || "عکس با موفقیت آپدیت شد.");
                if (data.avatar_url) {
                    const uniqueUrl = `${data.avatar_url}?t=${new Date().getTime()}`;
                    localStorage.setItem('userAvatar', uniqueUrl);

                    if (typeof fetchAndDisplayUserData === 'function') {
                        fetchAndDisplayUserData();
                    }

                    setTimeout(() => {
                        window.location.href = 'account.html';
                    }, 300);
                }
            } else {
                alert(`خطا: ${JSON.stringify(data)}`);
            }
        } catch (error) {
            console.error("Avatar update error:", error);
            alert("مشکل در ارتباط با سرور.");
        }
    });
});