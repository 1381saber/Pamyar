document.addEventListener('DOMContentLoaded', () => {


    const objectivesContainer = document.getElementById('objectives-container');
    const addObjectiveBtn = document.getElementById('add-objective-btn');
    const addObjectivePanel = document.getElementById('add-objective-panel');
    const addObjectiveForm = document.getElementById('add-objective-form');
    const cancelObjectiveBtn = document.getElementById('cancel-objective-btn');
    const addKrModal = document.getElementById('add-kr-modal-overlay');
    const addKrForm = document.getElementById('add-kr-form');
    const cancelKrBtn = document.getElementById('cancel-kr-btn');
    const krObjectiveIdInput = document.getElementById('kr-objective-id-input');

    if (!objectivesContainer) return;

    const API_BASE_URL = 'http://127.0.0.1:8000/api';
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
        window.location.href = 'login.html';
        return;
    }
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Token ${authToken}`
    };

    // ===============================================
    // ===          توابع ارتباط با بک‌اند (API)      ===
    // ===============================================

    const fetchObjectives = async() => {
        objectivesContainer.innerHTML = '<p>در حال بارگذاری اهداف...</p>';
        try {
            const response = await fetch(`${API_BASE_URL}/objectives/`, { headers: { 'Authorization': `Token ${authToken}` } });
            if (!response.ok) throw new Error('Failed to fetch objectives');
            const objectives = await response.json();
            renderObjectives(objectives);
        } catch (error) {
            console.error("Error fetching OKRs:", error);
            objectivesContainer.innerHTML = '<p class="empty-state visible">خطا در بارگذاری اهداف.</p>';
        }
    };

    const addObjective = async(title, quarter) => {
        try {
            await fetch(`${API_BASE_URL}/objectives/`, { method: 'POST', headers, body: JSON.stringify({ title, quarter }) });
            await fetchObjectives();
        } catch (error) {
            console.error("Error adding objective:", error);
            alert("مشکلی در افزودن هدف پیش آمد.");
        }
    };

    const deleteObjective = async(objId) => {
        if (!confirm("آیا از حذف این هدف و تمام نتایج کلیدی آن مطمئن هستید؟")) return;
        try {
            await fetch(`${API_BASE_URL}/objectives/${objId}/`, { method: 'DELETE', headers });
            await fetchObjectives();
        } catch (error) {
            console.error("Error deleting objective:", error);
            alert("مشکلی در حذف هدف پیش آمد.");
        }
    };

    const addKeyResult = async(objId, title, start, target) => {
        try {
            await fetch(`${API_BASE_URL}/objectives/${objId}/keyresults/`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ title, start_value: start, target_value: target })
            });
            await fetchObjectives();
        } catch (error) {
            console.error("Error adding Key Result:", error);
            alert("مشکلی در افزودن نتیجه کلیدی پیش آمد.");
        }
    };

    const updateKeyResultOnServer = async(krId, updates) => {
        try {
            const response = await fetch(`${API_BASE_URL}/keyresults/${krId}/`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify(updates)
            });
            if (!response.ok) {
                console.error(`Failed to update KR ${krId} on server. Response:`, await response.text());
                alert("خطا در همگام‌سازی با سرور. لطفاً صفحه را رفرش کنید.");
            }
        } catch (error) {
            console.error(`Network error updating KR ${krId}:`, error);
        }
    };

    const deleteKeyResult = async(krId) => {
        if (!confirm("آیا از حذف این نتیجه کلیدی مطمئن هستید؟")) return;
        try {
            await fetch(`${API_BASE_URL}/keyresults/${krId}/`, { method: 'DELETE', headers });
            await fetchObjectives();
        } catch (error) {
            console.error(`Error deleting KR ${krId}:`, error);
        }
    };

    // ===============================================
    // ===             تابع رندر اصلی              ===
    // ===============================================

    const renderObjectives = (objectives) => {
        objectivesContainer.innerHTML = '';
        if (objectives.length === 0) {
            objectivesContainer.innerHTML = '<p class="empty-state visible">هنوز هدفی تعریف نشده است.</p>';
            return;
        }

        objectives.forEach(obj => {
            const card = document.createElement('div');
            card.className = 'objective-card';

            let keyResultsHTML = '<div class="key-results-list">';
            (obj.key_results || []).forEach(kr => {
                keyResultsHTML += `
                    <div class="kr-item" id="kr-item-${kr.id}" data-start-value="${kr.start_value}" data-target-value="${kr.target_value}">
                        <div class="kr-content">
                            <div class="kr-item-actions">
                                <button type="button" class="kr-action-btn kr-delete-btn" data-id="${kr.id}" title="حذف"><img src="/pamyar_frontend/assets/delete-icon.svg" alt="حذف"></button>
                                <button type="button" class="kr-action-btn kr-edit-btn" data-id="${kr.id}" data-current="${kr.current_value}" title="ویرایش"><img src="/pamyar_frontend/assets/edit-icon.svg" alt="ویرایش"></button>
                            </div>
                            <div class="kr-values-fraction">
                                <span class="kr-current-value">${kr.current_value}</span>
                                <span class="kr-target-value">${kr.target_value}</span>
                            </div>
                            <div class="kr-info">
                                <span class="kr-title">${kr.title}</span>
                                <div class="kr-progress-bar-container"><div class="kr-progress-bar" style="width: ${kr.progress || 0}%;"></div></div>
                            </div>
                        </div>
                    </div>`;
            });
            keyResultsHTML += '</div>';

            card.innerHTML = `<div class="objective-header"><div><h2 class="objective-title">${obj.title}</h2><span class="objective-quarter">${obj.quarter}</span></div><button type="button" class="delete-objective-btn" data-id="${obj.id}">×</button></div>${keyResultsHTML}<div class="kr-actions"><button type="button" class="add-kr-btn" data-id="${obj.id}">+ افزودن نتیجه کلیدی</button></div>`;
            objectivesContainer.appendChild(card);
        });

        document.querySelectorAll('.delete-objective-btn').forEach(btn => btn.addEventListener('click', e => deleteObjective(e.target.closest('button').dataset.id)));
        document.querySelectorAll('.add-kr-btn').forEach(btn => btn.addEventListener('click', e => {
            krObjectiveIdInput.value = e.target.closest('button').dataset.id;
            addKrModal.classList.add('active');
        }));
        document.querySelectorAll('.kr-delete-btn').forEach(btn => btn.addEventListener('click', e => deleteKeyResult(e.target.closest('button').dataset.id)));

        document.querySelectorAll('.kr-edit-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                e.preventDefault();

                const button = e.target.closest('button');
                const krId = button.dataset.id;
                const currentValue = button.dataset.current;

                const newValueStr = prompt("مقدار فعلی جدید را وارد کنید:", currentValue);
                const newValue = parseFloat(newValueStr);

                if (newValueStr !== null && !isNaN(newValue)) {

                    const krItemElement = document.getElementById(`kr-item-${krId}`);
                    if (krItemElement) {
                        const currentValueSpan = krItemElement.querySelector('.kr-current-value');
                        const startValue = parseFloat(krItemElement.dataset.startValue);
                        const targetValue = parseFloat(krItemElement.dataset.targetValue);
                        const progressBar = krItemElement.querySelector('.kr-progress-bar');

                        currentValueSpan.textContent = newValue;
                        button.dataset.current = newValue;

                        let progress = 0;
                        if (targetValue !== startValue) {
                            progress = ((newValue - startValue) / (targetValue - startValue)) * 100;
                        } else if (newValue >= targetValue) {
                            progress = 100;
                        }
                        progress = Math.min(Math.max(progress, 0), 100);
                        progressBar.style.width = `${progress}%`;
                    }


                    updateKeyResultOnServer(krId, { current_value: newValue });
                }
            });
        });
    };


    // ===        مدیریت فرم‌ها و مودال              ===
    addObjectiveBtn.addEventListener('click', (e) => {
        e.preventDefault();
        addObjectivePanel.classList.toggle('open');
    });
    cancelObjectiveBtn.addEventListener('click', (e) => {
        e.preventDefault();
        addObjectivePanel.classList.remove('open');
    });

    addObjectiveForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const title = document.getElementById('objective-title-input').value;
        const quarter = document.getElementById('objective-quarter-input').value;
        if (title && quarter) {
            addObjective(title, quarter).then(() => {
                addObjectivePanel.classList.remove('open');
                addObjectiveForm.reset();
            });
        }
    });
    cancelKrBtn.addEventListener('click', (e) => {
        e.preventDefault();
        addKrModal.classList.remove('active');
    });
    addKrModal.addEventListener('click', e => {
        if (e.target === addKrModal) {
            e.preventDefault();
            addKrModal.classList.remove('active');
        }
    });
    addKrForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const objId = krObjectiveIdInput.value;
        const title = document.getElementById('kr-title-input').value;
        const start = parseFloat(document.getElementById('kr-start-input').value);
        const target = parseFloat(document.getElementById('kr-target-input').value);
        if (objId && title && !isNaN(start) && !isNaN(target)) {
            addKeyResult(objId, title, start, target).then(() => {
                addKrModal.classList.remove('active');
                addKrForm.reset();
            });
        }
    });

    fetchObjectives();
});