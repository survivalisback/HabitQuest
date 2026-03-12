const API_BASE = 'http://localhost:8000';

const STORAGE_TOKEN      = 'habitquest_token';
const STORAGE_USERNAME   = 'habitquest_username';
const STORAGE_GAMIF_PFX  = 'habitquest_gam_';

// ─── State ────────────────────────────────────────────────────────────────────
const state = {
  token:    null,
  username: null,
  habits:   [],
  gamification: {
    totalXp:          0,
    totalCompletions: 0,
    completionDates:  [],   // one ISO-date entry per completion event
    usedFrequencies:  [],
  },
  selectedFrequency: null,
  selectedDifficulty: null,
};

// ─── XP / Level System ───────────────────────────────────────────────────────
// Mirrors the backend's Level logic (difficulty * 10 * freq_multiplier)
// Level thresholds: cumulative total XP required to reach each level
const XP_THRESHOLDS = [0, 100, 250, 500, 900, 1500, 2500, 4000, 6000, 9000, 14000];

function getLevelInfo(totalXp) {
  let level = 1;
  for (let i = 1; i < XP_THRESHOLDS.length; i++) {
    if (totalXp >= XP_THRESHOLDS[i]) {
      level = i + 1;
    } else {
      const xpInLevel = totalXp - XP_THRESHOLDS[i - 1];
      const xpNeeded  = XP_THRESHOLDS[i] - XP_THRESHOLDS[i - 1];
      return { level, xpInLevel, xpNeeded };
    }
  }
  // Max level
  const last = XP_THRESHOLDS[XP_THRESHOLDS.length - 1];
  return { level, xpInLevel: totalXp - last, xpNeeded: 5000 };
}

const TITLES = [
  'Beginner', 'Apprentice', 'Journeyman', 'Adept',
  'Specialist', 'Expert', 'Master', 'Grandmaster', 'Legend', 'Mythic',
];

function getLevelTitle(level) {
  return TITLES[Math.min(level - 1, TITLES.length - 1)];
}

// ─── Streak Calculation ───────────────────────────────────────────────────────
function calculateStreak(dates) {
  if (!dates || dates.length === 0) return 0;
  const unique = [...new Set(dates)].sort().reverse(); // newest first
  const today  = new Date().toISOString().slice(0, 10);
  let streak   = 0;
  const cursor = new Date(today);

  for (const d of unique) {
    const expected = cursor.toISOString().slice(0, 10);
    if (d === expected) {
      streak++;
      cursor.setDate(cursor.getDate() - 1);
    } else if (d < expected) {
      break; // gap found
    }
  }
  return streak;
}

// ─── Gamification Persistence ─────────────────────────────────────────────────
function gamifKey() {
  return STORAGE_GAMIF_PFX + (state.username || 'anon');
}

function loadGamification() {
  try {
    const raw = localStorage.getItem(gamifKey());
    if (!raw) return;
    const parsed = JSON.parse(raw);
    // Prune completion dates older than 90 days to keep storage lean
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - 90);
    const cutoffStr = cutoff.toISOString().slice(0, 10);
    parsed.completionDates = (parsed.completionDates || []).filter(d => d >= cutoffStr);
    Object.assign(state.gamification, parsed);
  } catch { /* ignore */ }
}

function saveGamification() {
  try {
    localStorage.setItem(gamifKey(), JSON.stringify(state.gamification));
  } catch { /* ignore */ }
}

// ─── Auth ─────────────────────────────────────────────────────────────────────
function loadAuth() {
  state.token    = localStorage.getItem(STORAGE_TOKEN);
  state.username = localStorage.getItem(STORAGE_USERNAME);
  return !!(state.token && state.username);
}

function saveAuth(token, username) {
  state.token    = token;
  state.username = username;
  localStorage.setItem(STORAGE_TOKEN,    token);
  localStorage.setItem(STORAGE_USERNAME, username);
}

function clearAuth() {
  state.token    = null;
  state.username = null;
  localStorage.removeItem(STORAGE_TOKEN);
  localStorage.removeItem(STORAGE_USERNAME);
}

function authHeaders() {
  return { Authorization: `Bearer ${state.token}` };
}

// ─── API ──────────────────────────────────────────────────────────────────────
async function apiPost(path, params) {
  const url = `${API_BASE}${path}?${new URLSearchParams(params)}`;
  const res = await fetch(url, { method: 'POST', headers: authHeaders() });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json().catch(() => null);
}

async function apiDelete(path, params) {
  const url = `${API_BASE}${path}?${new URLSearchParams(params)}`;
  const res = await fetch(url, { method: 'DELETE', headers: authHeaders() });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }
}

async function apiFetchHabits() {
  const res = await fetch(`${API_BASE}/habits`, { headers: authHeaders() });
  if (res.status === 401) { clearAuth(); showLoginOverlay(); throw new Error('Session expired.'); }
  if (!res.ok) throw new Error('Failed to load habits.');
  return res.json();
}

async function apiLogin(username, password) {
  const res = await fetch(`${API_BASE}/login?${new URLSearchParams({ username, password })}`, { method: 'POST' });
  if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Login failed.'); }
  return res.json();
}

async function apiRegister(username, password) {
  const res = await fetch(`${API_BASE}/register?${new URLSearchParams({ username, password })}`, { method: 'POST' });
  if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Registration failed.'); }
  return res.json();
}

// ─── Feedback Banner ──────────────────────────────────────────────────────────
let feedbackTimer = null;
function showFeedback(msg, type = 'success') {
  const el = document.getElementById('feedback-banner');
  el.textContent = msg;
  el.className   = type;
  el.classList.remove('hidden');
  clearTimeout(feedbackTimer);
  feedbackTimer = setTimeout(() => el.classList.add('hidden'), 3200);
}

// ─── XP Toast ─────────────────────────────────────────────────────────────────
let toastTimer = null;
function showXpToast(xp) {
  const el = document.getElementById('xp-toast');
  el.textContent = `+${xp} XP`;
  el.className = 'toast-in';
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.className = 'toast-out';
    setTimeout(() => { el.className = 'hidden'; }, 350);
  }, 1600);
}

// ─── Gamification Render ──────────────────────────────────────────────────────
function renderGamification() {
  const { totalXp, totalCompletions, completionDates, usedFrequencies } = state.gamification;
  const { level, xpInLevel, xpNeeded } = getLevelInfo(totalXp);
  const streak = calculateStreak(completionDates);
  const today  = new Date().toISOString().slice(0, 10);

  document.getElementById('level-number').textContent    = level;
  document.getElementById('player-name').textContent     = state.username || 'Adventurer';
  document.getElementById('player-title').textContent    = getLevelTitle(level);
  document.getElementById('xp-text').textContent         = `${xpInLevel} / ${xpNeeded} XP`;
  document.getElementById('xp-bar-fill').style.width     = `${Math.min(100, (xpInLevel / xpNeeded) * 100)}%`;
  document.getElementById('streak-value').textContent    = streak;
  document.getElementById('completions-value').textContent = totalCompletions;

  // Today's progress (daily habits done today vs total daily habits)
  const dailyTotal   = state.habits.filter(h => h.frequency === 'daily').length;
  const todayCount   = completionDates.filter(d => d === today).length;
  document.getElementById('today-text').textContent      = `${Math.min(todayCount, dailyTotal)} / ${dailyTotal}`;
  const todayPct = dailyTotal > 0 ? Math.min(100, (todayCount / dailyTotal) * 100) : 0;
  document.getElementById('today-bar-fill').style.width  = `${todayPct}%`;

  // Achievements
  setAchievement('ach-first-step',   totalCompletions >= 1);
  setAchievement('ach-week-warrior', streak >= 7);
  setAchievement('ach-habit-master', state.habits.length >= 10);
  setAchievement('ach-consistent',   streak >= 30);
  setAchievement('ach-explorer',     ['daily', 'weekly', 'monthly'].every(f => usedFrequencies.includes(f)));
  setAchievement('ach-legend',       totalCompletions >= 100);
}

function setAchievement(id, unlocked) {
  document.getElementById(id)?.classList.toggle('locked', !unlocked);
}

// ─── Habit List Rendering ─────────────────────────────────────────────────────
function createHabitItem(habit) {
  const li = document.createElement('li');
  li.className    = 'habit-item';
  li.dataset.id   = habit.id;
  li.dataset.freq = habit.frequency;

  const label = document.createElement('label');
  const cb    = document.createElement('input');
  cb.type = 'checkbox';
  cb.addEventListener('change', handleHabitCheck);

  const nameSpan = document.createElement('span');
  nameSpan.className   = 'habit-name';
  nameSpan.textContent = habit.name;
  nameSpan.title       = habit.name;
  label.append(cb, nameSpan);

  // Difficulty dots
  const diff    = Math.max(1, Math.min(5, habit.difficulty || 1));
  const diffEl  = document.createElement('span');
  diffEl.className = 'diff-indicator';
  for (let i = 1; i <= 5; i++) {
    const dot = document.createElement('span');
    dot.className = 'diff-dot' + (i <= diff ? ' on' : '');
    diffEl.appendChild(dot);
  }

  // XP chip
  const xpEl = document.createElement('span');
  xpEl.className   = 'xp-chip';
  xpEl.textContent = `+${habit.xp_reward ?? diff * 10} XP`;

  // Delete button
  const del = document.createElement('button');
  del.className   = 'btn-delete-habit';
  del.textContent = '×';
  del.title       = 'Delete habit';
  del.addEventListener('click', handleDeleteHabit);

  li.append(label, diffEl, xpEl, del);
  return li;
}

function renderList(freq) {
  const ul      = document.getElementById(`list-${freq}`);
  const emptyEl = document.getElementById(`empty-${freq}`);
  const habits  = state.habits.filter(h => h.frequency === freq);

  ul.innerHTML = '';
  if (habits.length === 0) {
    emptyEl.textContent = `No ${freq} habits yet.`;
    emptyEl.classList.remove('hidden');
    return;
  }
  emptyEl.classList.add('hidden');
  habits.forEach(h => ul.appendChild(createHabitItem(h)));
}

function renderAllLists() {
  ['daily', 'weekly', 'monthly'].forEach(renderList);
}

// ─── Event Handlers ───────────────────────────────────────────────────────────
async function handleHabitCheck(e) {
  const cb      = e.target;
  const li      = cb.closest('.habit-item');
  const habitId = parseInt(li.dataset.id, 10);
  const habit   = state.habits.find(h => h.id === habitId);
  if (!habit) return;

  cb.disabled = true;

  try {
    const result = await apiPost('/toggleTaskCompletion', { id: habitId });
    const xp     = habit.xp_reward ?? (habit.difficulty * 10);
    const today  = new Date().toISOString().slice(0, 10);
    const g      = state.gamification;

    if (result.completed) {
      g.totalXp          += xp;
      g.totalCompletions += 1;
      g.completionDates.push(today);
      if (!g.usedFrequencies.includes(habit.frequency)) {
        g.usedFrequencies.push(habit.frequency);
      }
      saveGamification();
      showXpToast(xp);
      showFeedback(`"${habit.name}" completed! +${xp} XP`, 'success');
    } else {
      g.totalXp          = Math.max(0, g.totalXp - xp);
      g.totalCompletions = Math.max(0, g.totalCompletions - 1);
      const idx = g.completionDates.lastIndexOf(today);
      if (idx !== -1) g.completionDates.splice(idx, 1);
      saveGamification();
      showFeedback(`"${habit.name}" unmarked.`, 'success');
    }

    li.classList.add('completing');
    setTimeout(() => { renderAllLists(); renderGamification(); }, 420);
  } catch (err) {
    cb.disabled = false;
    cb.checked  = false;
    showFeedback(err.message || 'Failed to update habit.', 'error');
  }
}

async function handleDeleteHabit(e) {
  const li      = e.currentTarget.closest('.habit-item');
  const habitId = parseInt(li.dataset.id, 10);
  const freq    = li.dataset.freq;

  try {
    await apiDelete('/deleteTask', { id: habitId });
    state.habits = state.habits.filter(h => h.id !== habitId);
    renderList(freq);
    renderGamification();
    showFeedback('Habit deleted.', 'success');
  } catch (err) {
    showFeedback(err.message || 'Failed to delete habit.', 'error');
  }
}

async function handleAddRecurring() {
  const name = document.getElementById('habit-name-input').value.trim();
  if (!name) { showFeedback('Please enter a habit name.', 'error'); return; }
  if (!state.selectedFrequency) { showFeedback('Please choose a frequency.', 'error'); return; }

  const difficulty = state.selectedDifficulty ?? 1;

  try {
    await apiPost('/createTask', {
      name,
      description: '',
      frequency:   state.selectedFrequency,
      difficulty:  difficulty,
    });
    state.habits = await apiFetchHabits();
    renderAllLists();
    renderGamification();
    showFeedback(`"${name}" added as ${state.selectedFrequency} habit!`, 'success');
    document.getElementById('habit-name-input').value = '';
    hideRecurringConfig();
  } catch (err) {
    showFeedback(err.message || 'Failed to add habit.', 'error');
  }
}

function handleTrackNow() {
  const input = document.getElementById('habit-name-input');
  const name  = input.value.trim();
  if (!name) { showFeedback('Please enter a habit name.', 'error'); input.focus(); return; }
  // "Track now" = one-off, no backend persistence for one-time habits yet
  showFeedback(`"${name}" tracked!`, 'success');
  input.value = '';
}

// ─── Recurring Config UI ──────────────────────────────────────────────────────
function showRecurringConfig() {
  document.getElementById('recurring-config').classList.remove('hidden');
  document.querySelectorAll('.freq-btn, .diff-btn').forEach(b => b.classList.remove('active'));
  state.selectedFrequency  = null;
  state.selectedDifficulty = null;
}

function hideRecurringConfig() {
  document.getElementById('recurring-config').classList.add('hidden');
  state.selectedFrequency  = null;
  state.selectedDifficulty = null;
}

// ─── Login Overlay ────────────────────────────────────────────────────────────
function showLoginOverlay() {
  document.getElementById('login-overlay').classList.remove('hidden');
  document.getElementById('app').classList.add('hidden');
}

function hideLoginOverlay() {
  document.getElementById('login-overlay').classList.add('hidden');
  document.getElementById('app').classList.remove('hidden');
}

function setLoginError(msg) {
  const el = document.getElementById('login-error');
  if (msg) { el.textContent = msg; el.classList.remove('hidden'); }
  else      { el.classList.add('hidden'); }
}

function setLoginBusy(busy) {
  document.getElementById('btn-login').disabled    = busy;
  document.getElementById('btn-register').disabled = busy;
}

async function handleLogin() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  if (!username || !password) { setLoginError('Please enter username and password.'); return; }
  setLoginBusy(true);
  setLoginError(null);
  try {
    const data = await apiLogin(username, password);
    saveAuth(data.token, data.username || username);
    await loadApp();
    hideLoginOverlay();
  } catch (err) {
    setLoginError(err.message);
  } finally {
    setLoginBusy(false);
  }
}

async function handleRegister() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  if (!username || !password) { setLoginError('Please enter username and password.'); return; }
  if (password.length < 4)   { setLoginError('Password must be at least 4 characters.'); return; }
  setLoginBusy(true);
  setLoginError(null);
  try {
    const data = await apiRegister(username, password);
    saveAuth(data.token, data.username || username);
    await loadApp();
    hideLoginOverlay();
  } catch (err) {
    setLoginError(err.message);
  } finally {
    setLoginBusy(false);
  }
}

// ─── App Bootstrap ────────────────────────────────────────────────────────────
async function loadApp() {
  state.gamification = {
    totalXp: 0, totalCompletions: 0, completionDates: [], usedFrequencies: [],
  };
  loadGamification();
  document.getElementById('header-username').textContent = state.username || '';

  try {
    state.habits = await apiFetchHabits();
  } catch {
    state.habits = [];
  }

  renderAllLists();
  renderGamification();
}

// ─── Init ─────────────────────────────────────────────────────────────────────
function initApp() {
  // Auth check
  if (loadAuth()) {
    hideLoginOverlay();
    loadApp();
  } else {
    showLoginOverlay();
  }

  // Login / Register
  document.getElementById('btn-login').addEventListener('click', handleLogin);
  document.getElementById('btn-register').addEventListener('click', handleRegister);
  document.getElementById('login-username').addEventListener('keydown', e => {
    if (e.key === 'Enter') document.getElementById('login-password').focus();
  });
  document.getElementById('login-password').addEventListener('keydown', e => {
    if (e.key === 'Enter') handleLogin();
  });

  // Logout
  document.getElementById('btn-logout').addEventListener('click', () => {
    clearAuth();
    state.habits       = [];
    state.gamification = { totalXp: 0, totalCompletions: 0, completionDates: [], usedFrequencies: [] };
    showLoginOverlay();
  });

  // Habit actions
  document.getElementById('btn-track-now').addEventListener('click', handleTrackNow);
  document.getElementById('btn-add-recurring').addEventListener('click', () => {
    if (!document.getElementById('habit-name-input').value.trim()) {
      showFeedback('Please enter a habit name.', 'error');
      document.getElementById('habit-name-input').focus();
      return;
    }
    showRecurringConfig();
  });
  document.getElementById('btn-confirm-recurring').addEventListener('click', handleAddRecurring);
  document.getElementById('btn-cancel-recurring').addEventListener('click', hideRecurringConfig);

  // Frequency selection
  document.querySelectorAll('.freq-btn').forEach(btn =>
    btn.addEventListener('click', () => {
      document.querySelectorAll('.freq-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.selectedFrequency = btn.dataset.freq;
    })
  );

  // Difficulty selection
  document.querySelectorAll('.diff-btn').forEach(btn =>
    btn.addEventListener('click', () => {
      document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.selectedDifficulty = parseInt(btn.dataset.diff, 10);
    })
  );

  // Enter key in habit input
  document.getElementById('habit-name-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') handleTrackNow();
  });
}

document.addEventListener('DOMContentLoaded', initApp);
