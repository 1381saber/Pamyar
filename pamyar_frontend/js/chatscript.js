document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'http://127.0.0.1:8000/api';
    const authToken = localStorage.getItem('authToken');
    const pageBody = document.body;

    const fetchAndDisplayUserData = async() => {

        if (!authToken) {
            document.querySelectorAll('.profile-avatar, #avatar-preview-img').forEach(img => {
                img.src = '/pamyar_frontend/assets/my-default-avatar.png'; // مسیر صحیح عکس پیش‌فرض
            });
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/profile/`, {
                headers: { 'Authorization': `Token ${authToken}` }
            });

            if (response.ok) {
                const data = await response.json();


                document.querySelectorAll('.user-email').forEach(el => {
                    if (data.email) el.textContent = data.email;
                });


                if (data.avatar_url) {
                    const uniqueUrl = `${data.avatar_url}?t=${new Date().getTime()}`;
                    localStorage.setItem('userAvatar', uniqueUrl);
                    document.querySelectorAll('.profile-avatar, #avatar-preview-img').forEach(img => {
                        img.src = uniqueUrl;
                    });
                } else {

                    localStorage.removeItem('userAvatar');
                    document.querySelectorAll('.profile-avatar, #avatar-preview-img').forEach(img => {
                        img.src = '/pamyar_frontend/assets/my-default-avatar.png';
                    });
                }
            } else {

                localStorage.removeItem('authToken');
                localStorage.removeItem('userAvatar');

                if (!pageBody.classList.contains('login-page') && !pageBody.classList.contains('signup-page')) {
                    window.location.href = 'login.html';
                }
            }
        } catch (error) {
            console.error("Error fetching user profile data:", error);
        }
    };

    // --- اجرای اولیه در تمام صفحات ---
    const cachedAvatar = localStorage.getItem('userAvatar');
    if (cachedAvatar) {
        document.querySelectorAll('.profile-avatar, #avatar-preview-img').forEach(img => {
            img.src = cachedAvatar;
        });
    }

    fetchAndDisplayUserData();


    // ===============================================
    // ===     منطق مختص صفحه چت‌بات (chatbot.html)   ===
    // ===============================================

    if (pageBody.classList.contains('chatbot-page')) {

        console.log("--- CHATBOT SCRIPT INITIALIZED ---");

        const chatForm = document.getElementById('chat-form');
        const chatInput = document.getElementById('chat-input');
        const messagesContainer = document.getElementById('chat-messages');


        if (!chatForm || !chatInput || !messagesContainer) {
            console.error("Critical error: One or more essential chat elements are missing from the DOM.");
            return;
        }

        let chatHasStarted = false;

        const addMessageToUI = (text, senderClass) => {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('chat-bubble', senderClass);
            messageDiv.style.whiteSpace = 'pre-wrap';
            messageDiv.textContent = text;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            return messageDiv;
        };

        const showInitialContent = () => {
            if (messagesContainer.innerHTML.trim() === '') {
                messagesContainer.innerHTML = `
                    <div class="main-content-initial">
                        <img src="/pamyar_frontend/assets/main-orb.png" alt="لوگوی پمیار" class="main-orb-small">
                        <div class="prompt-text">
                            <p>پمیار اینجاست</p>
                            <p>چطور می‌توانم کمک کنم؟</p>
                        </div>
                    </div>
                `;
            }
        };
        showInitialContent();

        chatForm.addEventListener('submit', async(e) => {
            console.log("--- SUBMIT EVENT CAPTURED! ---");

            e.preventDefault();
            console.log("Default form submission prevented.");

            const userMessage = chatInput.value.trim();
            if (!userMessage) return;

            if (!chatHasStarted) {
                messagesContainer.innerHTML = '';
                chatHasStarted = true;
            }

            addMessageToUI(userMessage, 'user-message');
            chatInput.value = '';

            const thinkingBubble = addMessageToUI("در حال فکر کردن...", 'bot-message');

            try {
                const response = await fetch(`${API_BASE_URL}/chat/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Token ${authToken}` },
                    body: JSON.stringify({ message: userMessage })
                });

                thinkingBubble.remove();

                if (response.ok) {
                    const data = await response.json();
                    addMessageToUI(data.reply, 'bot-message');
                } else {
                    addMessageToUI("متاسفانه خطایی در پاسخگویی رخ داد.", 'bot-message');
                }
            } catch (error) {
                console.error("Chat Error:", error);
                if (thinkingBubble) thinkingBubble.remove();
                addMessageToUI("خطا در ارتباط با سرور چت.", 'bot-message');
            }

            console.log("--- SUBMIT HANDLER FINISHED ---. If page reloads now, the problem is external.");

        });

        const style = document.createElement('style');
        style.textContent = `
            .user-message {
                background-color: var(--color-text-secondary, #34495E);
                color: var(--color-accent-text, #FFFFFF);
                align-self: flex-start;
                border-bottom-left-radius: 4px;
            }
            .bot-message {
                background-color: var(--color-card-background, #FFFFFF);
                color: var(--color-text-primary, #2C3E50);
                align-self: flex-end;
                border-bottom-right-radius: 4px;
            }
        `;
        document.head.appendChild(style);
    }

});