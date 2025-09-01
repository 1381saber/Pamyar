document.addEventListener('DOMContentLoaded', () => {
    const passwordForm = document.getElementById('password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async(e) => {
            e.preventDefault();
            const old_password = document.getElementById('current-password').value;
            const new_password = document.getElementById('new-password').value;
            const authToken = localStorage.getItem('authToken');

            try {
                const response = await fetch('http://127.0.0.1:8000/api/profile/change-password/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Token ${authToken}` },
                    body: JSON.stringify({ old_password, new_password })
                });
                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    passwordForm.reset();
                } else {
                    alert(`خطا: ${data.error || JSON.stringify(data)}`);
                }
            } catch (error) {
                alert("مشکل در ارتباط با سرور.");
            }
        });
    }
});