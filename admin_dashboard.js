const API_BASE = (window.EVENT_API_BASE || '').replace(/\/$/, '');

const pendingBody = document.getElementById('pendingBody');
const pendingTable = document.getElementById('pendingTable');
const loadingEl = document.getElementById('loading');
const emptyState = document.getElementById('emptyState');
const statusMsg = document.getElementById('statusMsg');

document.getElementById('refreshBtn').addEventListener('click', loadPending);

function setStatus(text, isError = false) {
  statusMsg.textContent = text;
  statusMsg.classList.toggle('error', isError);
}

function formatWhen(iso) {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

function sourceLabel(event) {
  if (event.submission_type === 'instagram_scrap') {
    return `Instagram${event.ig_handle ? ` · @${event.ig_handle}` : ''}`;
  }
  const parts = ['User submitted'];
  if (event.submitter_name) parts.push(event.submitter_name);
  if (event.marketing_budget) parts.push(`Budget: ${event.marketing_budget}`);
  return parts.join(' · ');
}

function eventDetails(event) {
  const bits = [
    `<strong>${escapeHtml(event.summary)}</strong>`,
    `<span class="meta">${escapeHtml(event.location)}</span>`,
  ];
  if (event.description) {
    bits.push(`<span class="desc">${escapeHtml(event.description.slice(0, 160))}</span>`);
  }
  if (event.digital_media_notes) {
    bits.push(`<span class="meta">Digital media: ${escapeHtml(event.digital_media_notes)}</span>`);
  }
  if (event.source_url) {
    bits.push(`<a href="${escapeAttr(event.source_url)}" target="_blank" rel="noopener">Source</a>`);
  }
  return bits.join('<br>');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeAttr(str) {
  return escapeHtml(str).replace(/'/g, '&#39;');
}

async function loadPending() {
  loadingEl.hidden = false;
  pendingTable.hidden = true;
  emptyState.hidden = true;
  setStatus('');

  try {
    const res = await fetch(`${API_BASE}/api/admin/events/pending`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const events = await res.json();

    pendingBody.innerHTML = '';
    if (!events.length) {
      emptyState.hidden = false;
      return;
    }

    events.forEach((event) => {
      const tr = document.createElement('tr');
      tr.dataset.id = event.id;
      tr.innerHTML = `
        <td class="when">${formatWhen(event.start_time)}</td>
        <td class="detail">${eventDetails(event)}</td>
        <td class="source"><span class="badge ${event.submission_type}">${sourceLabel(event)}</span></td>
        <td class="actions">
          <button type="button" class="btn-approve" data-id="${event.id}">Approve</button>
          <button type="button" class="btn-reject" data-id="${event.id}">Reject</button>
        </td>
      `;
      pendingBody.appendChild(tr);
    });

    pendingTable.hidden = false;
    pendingBody.querySelectorAll('.btn-approve').forEach((btn) => {
      btn.addEventListener('click', () => reviewEvent(btn.dataset.id, 'approve'));
    });
    pendingBody.querySelectorAll('.btn-reject').forEach((btn) => {
      btn.addEventListener('click', () => reviewEvent(btn.dataset.id, 'reject'));
    });
  } catch (err) {
    setStatus(`Failed to load: ${err.message}`, true);
  } finally {
    loadingEl.hidden = true;
  }
}

async function reviewEvent(id, action) {
  const row = pendingBody.querySelector(`tr[data-id="${id}"]`);
  if (row) row.classList.add('busy');

  try {
    const res = await fetch(`${API_BASE}/api/admin/events/${id}/${action}`, { method: 'POST' });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
    setStatus(data.message || `Event ${id} ${action}d.`);
    if (row) row.remove();
    if (!pendingBody.children.length) {
      pendingTable.hidden = true;
      emptyState.hidden = false;
    }
  } catch (err) {
    setStatus(err.message, true);
    if (row) row.classList.remove('busy');
  }
}

loadPending();
