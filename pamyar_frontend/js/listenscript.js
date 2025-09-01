document.addEventListener('DOMContentLoaded', () => {

    const historyListContainer = document.querySelector('.history-list');
    if (!historyListContainer) {
        return;
    }

    const API_BASE_URL = 'http://127.0.0.1:8000';
    const authToken = localStorage.getItem('authToken');

    if (!authToken) {
        window.location.href = 'login.html';
        return;
    }

    let currentlyPlayingAudio = null;

    const deleteVoiceNote = async(noteId) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/history/voice/${noteId}/`, {
                method: 'DELETE',
                headers: { 'Authorization': `Token ${authToken}` }
            });

            if (response.ok) {
                const cardToRemove = document.querySelector(`.voice-item-card[data-id="${noteId}"]`);
                if (cardToRemove) {
                    cardToRemove.remove();
                }

                if (historyListContainer.children.length === 0) {
                    historyListContainer.innerHTML = '<p class="empty-state visible">هیچ ویس ضبط شده‌ای وجود ندارد.</p>';
                }
            } else {
                alert("مشکلی در حذف ویس پیش آمد.");
            }
        } catch (error) {
            console.error("خطای شبکه هنگام حذف:", error);
        }
    };

    const createVoiceCard = (note) => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'voice-item-card';
        cardDiv.dataset.id = note.id;
        const audio = new Audio(note.audio_file);

        let avatarSrc = localStorage.getItem('userAvatar') || '/pamyar_frontend/assets/my-default-avatar.png';


        const playIconSrc = '/pamyar_frontend/assets/play-icon.svg';
        const pauseIconSrc = '/pamyar_frontend/assets/pause-icon.svg';
        const staticWaveformSrc = '/pamyar_frontend/assets/waveform.svg';
        const animatedWaveformSrc = '/pamyar_frontend/assets/waveform-animated.gif';


        cardDiv.innerHTML = `
            <div class="voice-player">
                <div class="play-button-container">
                    <button class="play-pause-btn" aria-label="پخش"><img src="${playIconSrc}" alt="پخش"></button>
                    <button class="delete-voice-btn" aria-label="حذف ویس"><img src="/pamyar_frontend/assets/delete-icon.svg" alt="حذف"></button>
                </div>
                <img src="${staticWaveformSrc}" class="waveform-img" alt="موج صدا">
                <div class="profile-button profile-button--small">
                    <img src="${avatarSrc}" alt="آواتار" class="profile-avatar">
                    <div class="notification-badge"><img src="/pamyar_frontend/assets/check-icon.svg" alt="تایید شده"></div>
                </div>
            </div>
        `;

        const deleteBtn = cardDiv.querySelector('.delete-voice-btn');
        const playPauseBtn = cardDiv.querySelector('.play-pause-btn');
        const playIcon = playPauseBtn.querySelector('img');
        const waveformImg = cardDiv.querySelector('.waveform-img');

        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const confirmDelete = confirm("آیا از حذف این مکالمه مطمئن هستید؟");
            if (confirmDelete) {
                deleteVoiceNote(note.id);
            }
        });

        playPauseBtn.addEventListener('click', () => {
            if (currentlyPlayingAudio && currentlyPlayingAudio !== audio) {
                currentlyPlayingAudio.pause();
            }
            if (audio.paused) {
                audio.play();
                currentlyPlayingAudio = audio;
            } else {
                audio.pause();
            }
        });

        const stopPlaybackUI = () => {
            playIcon.src = playIconSrc;
            waveformImg.src = staticWaveformSrc;
        };

        audio.onplaying = () => {
            document.querySelectorAll('.voice-item-card .play-pause-btn img').forEach(img => img.src = playIconSrc);
            document.querySelectorAll('.voice-item-card .waveform-img').forEach(img => img.src = staticWaveformSrc);
            playIcon.src = pauseIconSrc;
            waveformImg.src = animatedWaveformSrc;
        };
        audio.onpause = stopPlaybackUI;
        audio.onended = () => {
            stopPlaybackUI();
            currentlyPlayingAudio = null;
        };

        return cardDiv;
    };
    const loadAndRenderHistory = async() => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/history/voice/`, {
                headers: { 'Authorization': `Token ${authToken}` }
            });
            if (!response.ok) throw new Error('Failed to fetch');
            const notes = await response.json();
            historyListContainer.innerHTML = '';
            if (notes.length === 0) {
                historyListContainer.innerHTML = '<p class="empty-state visible">هیچ ویس ضبط شده‌ای وجود ندارد.</p>';
            } else {
                notes.forEach(note => {
                    const card = createVoiceCard(note);
                    historyListContainer.appendChild(card);
                });
            }
        } catch (error) {
            console.error("خطا در بارگذاری تاریخچه:", error);
        }
    };

    loadAndRenderHistory();
});