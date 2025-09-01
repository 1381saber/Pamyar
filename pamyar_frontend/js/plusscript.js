document.addEventListener('DOMContentLoaded', () => {

    // --- منطق مودال پاپ‌آپ ---
    const openModalBtn = document.getElementById('open-modal-btn');
    if (openModalBtn) {
        const closeModalBtn = document.getElementById('close-modal-btn');
        const modalOverlay = document.getElementById('history-modal-overlay');

        openModalBtn.addEventListener('click', () => modalOverlay.classList.add('active'));

        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', () => modalOverlay.classList.remove('active'));
        }

        if (modalOverlay) {
            modalOverlay.addEventListener('click', (e) => {
                if (e.target === modalOverlay) modalOverlay.classList.remove('active');
            });
        }
    }
});