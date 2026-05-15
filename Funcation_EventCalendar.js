const EVENTS = [
  { date: '2026-05-15', title: 'PHX Zine vol. 3 drop',        type: 'zine',  venue: "Bragg's Pie Factory",    ig: '@phxzine' },
  { date: '2026-05-17', title: 'Suns playoff watch party',    type: 'suns',  venue: 'Footprint Center',        ig: '@suns' },
  { date: '2026-05-20', title: 'AZ Trading Card Show',        type: 'card',  venue: 'Mesa Convention Ctr',     ig: '@aztradingcards' },
  { date: '2026-05-22', title: 'First Friday Phoenix',        type: 'local', venue: 'Roosevelt Row',           ig: '@firstfridayphx' },
  { date: '2026-05-24', title: 'Interview release: Local artist', type: 'zine', venue: 'Online',              ig: '@phxzine' },
  { date: '2026-05-28', title: 'Suns game night',             type: 'suns',  venue: 'Footprint Center',        ig: '@suns' },
  { date: '2026-06-01', title: 'Zine swap meet',              type: 'zine',  venue: 'Changing Hands Bookstore',ig: '@phxzine' },
  { date: '2026-06-05', title: 'PHX Card collectors meet',    type: 'card',  venue: 'Scottsdale Quarter',      ig: '@aztradingcards' },
  { date: '2026-06-07', title: 'First Saturday art walk',     type: 'local', venue: 'Grand Ave',               ig: '@grandavephx' },
  { date: '2026-06-12', title: 'Limited trading card drop',   type: 'card',  venue: 'Online / DM',             ig: '@phxzine' },
  { date: '2026-06-15', title: 'Summer zine workshop',        type: 'zine',  venue: 'Civic Space Park',        ig: '@phxzine' },
  { date: '2026-06-20', title: 'AZ Sports collectibles fair', type: 'suns',  venue: 'PHX Convention Ctr',      ig: '@azsports' },
];

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

render();