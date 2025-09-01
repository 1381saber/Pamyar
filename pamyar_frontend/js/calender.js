document.addEventListener('DOMContentLoaded', () => {
    const monthYearTitle = document.getElementById('month-year-title');
    const daysGrid = document.getElementById('calendar-days-grid');
    const prevMonthBtn = document.getElementById('prev-month-btn');
    const nextMonthBtn = document.getElementById('next-month-btn');

    let currentDate = new Date();

    const renderCalendar = (date) => {
        const year = date.getFullYear();
        const month = date.getMonth();

        const persianMonths = ["ژانویه", "فبریه", "مارس", "آوریل", "می", "ژوئن", "جولای", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"];
        monthYearTitle.textContent = `${persianMonths[month]} ${year}`;

        daysGrid.innerHTML = '';

        const firstDayOfMonth = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();


        const startDayIndex = (firstDayOfMonth + 1) % 7;


        for (let i = 0; i < startDayIndex; i++) {
            daysGrid.appendChild(document.createElement('div'));
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'calendar-day';
            dayCell.textContent = day;

            const today = new Date();

            if (day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
                dayCell.classList.add('today');
            }

            dayCell.addEventListener('click', () => {

                document.querySelectorAll('.calendar-day.selected').forEach(cell => {
                    cell.classList.remove('selected');
                });

                dayCell.classList.add('selected');
                console.log(`تاریخ انتخاب شده: ${year}-${month + 1}-${day}`);
            });

            daysGrid.appendChild(dayCell);
        }
    };

    prevMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });

    nextMonthBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
    });

    renderCalendar(currentDate);
});