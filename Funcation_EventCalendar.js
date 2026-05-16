const API_BASE = 'http://localhost:8000';
let EVENTS = [];

async function loadEvents() {
  try {
    const res = await fetch(`${API_BASE}/api/events`);
    const data = await res.json();
    EVENTS = data.map(e => ({
      date: e.start_time.split('T')[0],
      title: e.summary,
      type: e.event_type || 'local',
      venue: e.location,
      ig: e.ig_handle ? `@${e.ig_handle}` : '',
    }));
  } catch (err) {
    console.error('Failed to load events:', err);
    EVENTS = [];
  }
  render();
}

loadEvents();

let currentDate = new Date(2026, 4, 1);
let activeFilter = 'all';

function toggleFilter(btn, type) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  activeFilter = type;
  render();
}

function filteredEvents() {
  return activeFilter === 'all' ? EVENTS : EVENTS.filter(e => e.type === activeFilter);
}

function changeMonth(dir) {
  currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + dir, 1);
  render();
}

function render() {
  const year     = currentDate.getFullYear();
  const month    = currentDate.getMonth();
  const today    = new Date();
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrev  = new Date(year, month, 0).getDate();

  document.getElementById('monthLabel').textContent =
    currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });

  const grid = document.getElementById('calGrid');
  grid.innerHTML = '';

  ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].forEach(d => {
    const dn = document.createElement('div');
    dn.className = 'day-name';
    dn.textContent = d;
    grid.appendChild(dn);
  });

  const total = Math.ceil((firstDay + daysInMonth) / 7) * 7;

  for (let i = 0; i < total; i++) {
    const cell = document.createElement('div');
    cell.className = 'day-cell';
    let dayNum, cellDate;

    if (i < firstDay) {
      dayNum   = daysInPrev - firstDay + i + 1;
      cellDate = new Date(year, month - 1, dayNum);
      cell.classList.add('other-month');
    } else if (i >= firstDay + daysInMonth) {
      dayNum   = i - firstDay - daysInMonth + 1;
      cellDate = new Date(year, month + 1, dayNum);
      cell.classList.add('other-month');
    } else {
      dayNum   = i - firstDay + 1;
      cellDate = new Date(year, month, dayNum);
      if (cellDate.toDateString() === today.toDateString()) cell.classList.add('today');
    }

    const numEl = document.createElement('div');
    numEl.className = 'day-num';
    numEl.textContent = dayNum;
    cell.appendChild(numEl);

    const dateStr = `${cellDate.getFullYear()}-${String(cellDate.getMonth()+1).padStart(2,'0')}-${String(cellDate.getDate()).padStart(2,'0')}`;
    const dayEvents = filteredEvents().filter(e => e.date === dateStr);

    dayEvents.slice(0, 2).forEach(ev => {
      const dot = document.createElement('div');
      dot.className = `event-dot ${ev.type}`;
      dot.textContent = ev.title;
      dot.title = `${ev.title} — ${ev.venue}`;
      cell.appendChild(dot);
    });

    if (dayEvents.length > 2) {
      const more = document.createElement('div');
      more.className = 'event-dot more';
      more.textContent = `+${dayEvents.length - 2} more`;
      cell.appendChild(more);
    }

    grid.appendChild(cell);
  }

  renderList();
}

function renderList() {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const upcoming = filteredEvents()
    .filter(e => new Date(e.date) >= today)
    .sort((a, b) => new Date(a.date) - new Date(b.date))
    .slice(0, 5);

  const list = document.getElementById('eventList');
  list.innerHTML = '';

  upcoming.forEach(ev => {
    const d    = new Date(ev.date);
    const item = document.createElement('div');
    item.className = 'event-list-item';
    item.innerHTML = `
      <div class="event-date-badge">
        <div class="eday">${d.getDate()}</div>
        <div class="emon">${d.toLocaleString('default', { month: 'short' })}</div>
      </div>
      <div class="event-info">
        <div class="etitle">${ev.title} <span class="insta-badge">${ev.ig}</span></div>
        <div class="emeta">📍 ${ev.venue}</div>
      </div>
    `;
    list.appendChild(item);
  });
}
