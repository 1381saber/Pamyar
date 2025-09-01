// microph.js (نسخه نهایی با پیام‌های فارسی)

document.addEventListener('DOMContentLoaded', () => {

    const listeningTextElement = document.querySelector('.listening-text');
    const stopListeningButton = document.querySelector('a > .footer-orb-active');

    if (!stopListeningButton || !listeningTextElement) {
        return;
    }

    const statusTranslations = {
        "Successfully connected to Pamyar AI server!": "با موفقیت متصل شدید!",
        "Starting Gemini Chatter session...": "در حال آماده‌سازی پمیار...",
        "🎙️  Pamyar is ready. Start speaking...": "پمیار آماده است. صحبت کنید...",
        "🔗 Connected to WebSocket.": "در حال برقراری ارتباط...",
        "✅ Session setup complete.": "آماده دریافت دستور",
        "[User speech detected...]": "صدای شما دریافت شد...",
        "[End of speech. Processing...]": "در حال پردازش...",
        "[Pamyar is speaking...]": "پمیار در حال پاسخگویی است...",
        "[You can speak now...]": "می‌توانید صحبت کنید...",
        "🎤 Microphone closed.": "جلسه پایان یافت.",
        "Stopping Gemini Chatter session...": "در حال پایان دادن به جلسه..."
    };

    const transcriptPreviewElement = document.createElement('p');
    transcriptPreviewElement.className = 'transcript-preview';
    listeningTextElement.parentElement.appendChild(transcriptPreviewElement);

    const socket = io('http://127.0.0.1:5001');

    // --- مدیریت رویدادهای SocketIO ---

    socket.on('connect', () => {
        console.log('اتصال به سرور پمیار برقرار شد.');
        socket.emit('start_chat', {});
    });

    socket.on('disconnect', () => {
        console.log('اتصال با سرور پمیار قطع شد.');
        if (listeningTextElement) listeningTextElement.textContent = "اتصال قطع شد.";
    });

    socket.on('status_update', (data) => {
        console.log("Original status from server:", data.message);

        const translatedMessage = statusTranslations[data.message] || data.message;

        if (listeningTextElement) {
            listeningTextElement.textContent = translatedMessage;
        }
    });

    socket.on('transcript_update', (data) => {
        console.log("Transcript from server:", data.transcript, "Is Final:", data.is_final);
        if (transcriptPreviewElement) {
            transcriptPreviewElement.textContent = data.transcript;

            if (data.is_final) {
                setTimeout(() => {
                    if (transcriptPreviewElement) transcriptPreviewElement.textContent = '';
                }, 3000);
            }
        }
    });
    // --- مدیریت اقدامات کاربر ---
    stopListeningButton.parentElement.addEventListener('click', () => {
        console.log("دکمه توقف کلیک شد. ارسال رویداد 'stop_chat'...");
        socket.emit('stop_chat', {});
    });

    const cleanupOnPageExit = () => {
        if (socket.connected) {
            console.log("صفحه در حال بسته شدن است. پاکسازی منابع سرور...");
            socket.emit('stop_chat', {});
            socket.disconnect();
        }
    };
    window.addEventListener('beforeunload', cleanupOnPageExit);
});