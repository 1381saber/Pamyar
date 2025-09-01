// todoscript.js

document.addEventListener('DOMContentLoaded', () => {

    const todoForm = document.getElementById('todo-form');
    if (!todoForm) return;

    const todoInput = document.getElementById('todo-input');
    const todoListContainer = document.getElementById('todo-list');
    const emptyState = document.getElementById('empty-state');
    const tagSelector = document.querySelector('.tag-selector');
    let activeTag = 'product'; // تگ پیش‌فرض

    const API_BASE_URL = 'http://127.0.0.1:8000/api';
    const authToken = localStorage.getItem('authToken');

    if (!authToken) {
        window.location.href = 'login.html';
        return;
    }

    // ===========================================
    // ===   توابع ارتباط با بک‌اند (API Calls)   ===
    // ===========================================

    // --- دریافت تمام کارها ---
    const fetchTasks = async() => {
        try {
            const response = await fetch(`${API_BASE_URL}/todos/`, {
                headers: { 'Authorization': `Token ${authToken}` }
            });
            if (response.status === 401) {
                localStorage.removeItem('authToken');
                window.location.href = 'login.html';
                return;
            }
            const tasks = await response.json();
            renderTasks(tasks);
        } catch (error) { console.error('Error fetching tasks:', error); }
    };

    // --- افزودن یک کار جدید ---
    const addTask = async(taskText, taskTag) => {
        try {
            await fetch(`${API_BASE_URL}/todos/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${authToken}`
                },
                body: JSON.stringify({ text: taskText, tag: taskTag })
            });
            await fetchTasks();
            todoInput.value = '';
        } catch (error) { console.error('Error adding task:', error); }
    };


    const updateTask = async(taskId, isCompleted) => {
        try {
            await fetch(`${API_BASE_URL}/todos/${taskId}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${authToken}`
                },
                body: JSON.stringify({ completed: isCompleted })
            });
        } catch (error) { console.error('Error updating task:', error); }
    };

    // --- حذف یک کار ---
    const deleteTask = async(taskId) => {
        try {
            await fetch(`${API_BASE_URL}/todos/${taskId}/`, {
                method: 'DELETE',
                headers: { 'Authorization': `Token ${authToken}` }
            });
        } catch (error) { console.error('Error deleting task:', error); }
    };

    // ===========================================
    // ===    بخش رندر و Event Listener ها        ===
    // ===========================================

    // --- تابع رندر کردن کارها (بدون تغییر) ---
    const renderTasks = (tasks) => {
        todoListContainer.innerHTML = '';
        if (!tasks || tasks.length === 0) {
            emptyState.classList.add('visible');
        } else {
            emptyState.classList.remove('visible');
            tasks.forEach(task => {
                const taskElement = document.createElement('div');
                taskElement.classList.add('todo-item');
                if (task.completed) taskElement.classList.add('completed');
                taskElement.dataset.id = task.id;

                const tagIndicator = `<div class="task-tag-indicator tag-${task.tag}"></div>`;

                taskElement.innerHTML = `
                    ${tagIndicator}
                    <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''}>
                    <span class="task-text">${task.text}</span>
                    <button class="delete-btn" aria-label="حذف کار">
                        <img src="/pamyar_frontend/assets/delete-icon.svg" alt="حذف">
                    </button>
                `;
                todoListContainer.appendChild(taskElement);
            });
        }
    };

    todoForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const taskText = todoInput.value.trim();
        if (taskText) {
            addTask(taskText, activeTag);
        }
    });

    todoListContainer.addEventListener('click', (e) => {
        const target = e.target;
        const parentTaskElement = target.closest('.todo-item');
        if (!parentTaskElement) return;

        const taskId = parentTaskElement.dataset.id;

        // **تیک زدن**
        if (target.classList.contains('task-checkbox')) {
            const isCompleted = target.checked;
            parentTaskElement.classList.toggle('completed', isCompleted);
            updateTask(taskId, isCompleted);
        }

        // **حذف کردن**
        else if (target.closest('.delete-btn')) {
            parentTaskElement.remove();
            deleteTask(taskId);
        }
    });


    if (tagSelector) {
        tagSelector.addEventListener('click', (e) => {
            if (e.target.matches('.tag-btn')) {
                tagSelector.querySelectorAll('.tag-btn').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
                activeTag = e.target.dataset.tag;
            }
        });
    }
    fetchTasks();
});