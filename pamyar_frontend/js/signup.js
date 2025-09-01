document.addEventListener('DOMContentLoaded', () => {
    // --- منطق فرم ثبت‌نام ---
    const API_BASE_URL = 'http://127.0.0.1:8000/api'
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async(event) => {
            event.preventDefault();
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;

            try {
                const response = await fetch(`${API_BASE_URL}/signup/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    alert(data.message || 'ثبت نام موفق بود. لطفاً وارد شوید.');
                    window.location.href = 'login.html';
                } else {
                    let errorMessages = [];
                    for (const key in data) {
                        errorMessages.push(`${data[key].join(', ')}`);
                    }
                    alert(`خطا در ثبت نام: ${errorMessages.join('\n')}`);
                }
            } catch (error) {
                console.error('Error during signup fetch:', error);
                alert('مشکلی در ارتباط با سرور هنگام ثبت نام پیش آمد.');
            }
        });
    }
});