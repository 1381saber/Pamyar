// chathistory.js

document.addEventListener('DOMContentLoaded', () => {

    const historyContainer = document.getElementById('chat-history-container');

    if (!historyContainer) {
        return;
    }

    const API_BASE_URL = 'http://127.0.0.1:8000/api';
    const authToken = localStorage.getItem('authToken');

    if (!authToken) {
        window.location.href = 'login.html';
        return;
    }


    const fetchAndRenderChatHistory = async() => {

        historyContainer.innerHTML = '<p style="text-align: center; margin-top: 20px;">در حال بارگذاری تاریخچه...</p>';

        try {
            const response = await fetch(`${API_BASE_URL}/history/chat/`, {
                headers: { 'Authorization': `Token ${authToken}` }
            });

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const historyData = await response.json();


            historyContainer.innerHTML = '';

            if (historyData.length === 0) {
                historyContainer.innerHTML = '<p class="empty-state visible" style="margin-top: 20px;">تاریخچه چتی برای نمایش وجود ندارد.</p>';
                return;
            }


            historyData.forEach(chat => {

                const userBubble = document.createElement('div');
                userBubble.classList.add('chat-bubble', 'user-message');
                userBubble.textContent = chat.user_prompt;
                userBubble.style.whiteSpace = 'pre-wrap';
                historyContainer.appendChild(userBubble);


                const modelBubble = document.createElement('div');
                modelBubble.classList.add('chat-bubble', 'bot-message');
                modelBubble.textContent = chat.model_response;
                modelBubble.style.whiteSpace = 'pre-wrap';
                historyContainer.appendChild(modelBubble);
            });


            window.scrollTo(0, document.body.scrollHeight);

        } catch (error) {
            console.error("Error fetching or rendering chat history:", error);
            historyContainer.innerHTML = '<p class="empty-state visible" style="margin-top: 20px;">خطا در بارگذاری تاریخچه.</p>';
        }
    };

    fetchAndRenderChatHistory();
});