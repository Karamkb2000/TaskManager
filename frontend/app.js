const API = '/api';

async function fetchTasks() {
  try {
    const res = await fetch(`${API}/tasks`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderTasks(data.tasks);
    updateCacheBadge(data.source);
  } catch (e) {
    document.getElementById('task-list').innerHTML =
      `<p class="error">Cannot reach the backend.<br>Make sure all containers are running: <code>docker-compose up --build</code></p>`;
  }
}

async function fetchStats() {
  try {
    const res = await fetch(`${API}/stats`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const d = await res.json();
    document.getElementById('s-total').textContent   = d.total_tasks;
    document.getElementById('s-done').textContent    = d.done_tasks;
    document.getElementById('s-pending').textContent = d.pending_tasks;
    document.getElementById('s-hits').textContent    = d.redis_hits;
    document.getElementById('s-misses').textContent  = d.redis_misses;
  } catch (e) {
    // stats are non-critical, fail silently
  }
}

function updateCacheBadge(source) {
  const badge = document.getElementById('cache-badge');
  if (source === 'cache') {
    badge.textContent = '⚡ Served from Redis cache';
    badge.className = 'badge cache';
  } else {
    badge.textContent = '🗄 Served from PostgreSQL';
    badge.className = 'badge db';
  }
}

function renderTasks(tasks) {
  const list = document.getElementById('task-list');
  if (!tasks || tasks.length === 0) {
    list.innerHTML = '<p class="empty">No tasks yet. Add one above!</p>';
    return;
  }
  list.innerHTML = tasks.map(task => `
    <div class="task-item ${task.done ? 'done' : ''}" id="task-${task.id}">
      <input
        class="task-checkbox"
        type="checkbox"
        ${task.done ? 'checked' : ''}
        onchange="toggleTask(${task.id})"
        title="Mark as ${task.done ? 'pending' : 'done'}"
      />
      <div class="task-body">
        <div class="task-title">${escapeHtml(task.title)}</div>
        ${task.description
          ? `<div class="task-desc">${escapeHtml(task.description)}</div>`
          : ''}
        <div class="task-meta">Created: ${formatDate(task.created_at)}</div>
      </div>
      <button
        class="delete-btn"
        onclick="deleteTask(${task.id})"
        title="Delete task"
      >&#215;</button>
    </div>
  `).join('');
}

async function toggleTask(id) {
  try {
    const res = await fetch(`${API}/tasks/${id}`, { method: 'PATCH' });
    if (!res.ok) throw new Error();
    fetchTasks();
    fetchStats();
  } catch (e) {
    alert('Could not update task. Try again.');
  }
}

async function deleteTask(id) {
  try {
    const res = await fetch(`${API}/tasks/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error();
    const el = document.getElementById(`task-${id}`);
    if (el) { el.style.opacity = '0'; el.style.transition = 'opacity 0.2s'; }
    setTimeout(() => { fetchTasks(); fetchStats(); }, 220);
  } catch (e) {
    alert('Could not delete task. Try again.');
  }
}

document.getElementById('task-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const titleInput = document.getElementById('title');
  const descInput  = document.getElementById('description');
  const btn        = e.target.querySelector('button');

  const title       = titleInput.value.trim();
  const description = descInput.value.trim();
  if (!title) return;

  btn.disabled = true;
  btn.textContent = 'Adding...';

  try {
    const res = await fetch(`${API}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, description })
    });
    if (!res.ok) throw new Error();
    titleInput.value = '';
    descInput.value  = '';
    fetchTasks();
    fetchStats();
  } catch (e) {
    alert('Could not add task. Try again.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Add Task';
  }
});

function escapeHtml(str) {
  return String(str)
    .replace(/&/g,  '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/"/g,  '&quot;');
}

function formatDate(str) {
  try { return new Date(str).toLocaleString(); }
  catch { return str; }
}

fetchTasks();
fetchStats();
setInterval(fetchStats, 10000);
