const API_BASE = 'http://localhost:8000';

const STORAGE_TOKEN      = 'habitquest_token';
const STORAGE_USERNAME   = 'habitquest_username';

// ─── State ────────────────────────────────────────────────────────────────────
const state = {
  token:    null,
  username: null,
  habits:   [],
  profile:  null,  // fetched from backend
  selectedFrequency: null,
};

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

async function apiFetchProfile() {
  const res = await fetch(`${API_BASE}/profile`, { headers: authHeaders() });
  if (res.status === 401) { clearAuth(); showLoginOverlay(); throw new Error('Session expired.'); }
  if (!res.ok) throw new Error('Failed to load profile.');
  return res.json();
}

async function apiLogin(username, password) {
  const res = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Login failed.'); }
  return res.json();
}

async function apiRegister(username, password) {
  const res = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
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
function showXpToast(xp, bonusXp) {
  const container = document.getElementById('xp-toast-container');
  const el = document.createElement('div');
  el.className = 'xp-toast';

  let text = `+${xp} XP`;
  if (bonusXp && bonusXp > 0) {
    text += ` (+${bonusXp} streak bonus)`;
  }
  el.textContent = text;

  container.appendChild(el);

  // Fade out then remove
  setTimeout(() => {
    el.classList.add('toast-out');
    setTimeout(() => el.remove(), 600);
  }, 2000);
}

// ─── Gamification Render ──────────────────────────────────────────────────────
function renderGamification() {
  const profile = state.profile;
  if (!profile) return;

  const { level_info, total_xp, total_completions } = profile;
  const { level, title, xp_in_level, xp_needed } = level_info;

  document.getElementById('level-number').textContent    = level;
  document.getElementById('player-name').textContent     = state.username || 'Adventurer';
  document.getElementById('player-title').textContent    = title;
  document.getElementById('xp-text').textContent         = `${xp_in_level} / ${xp_needed} XP`;
  document.getElementById('xp-bar-fill').style.width     = `${Math.min(100, (xp_in_level / xp_needed) * 100)}%`;

  // Best streak from habits
  const bestStreak = state.habits.reduce((max, h) => Math.max(max, h.streak || 0), 0);
  document.getElementById('streak-value').textContent    = bestStreak;
  document.getElementById('completions-value').textContent = total_completions;

  // Today's progress (daily habits with streaks covering today)
  const dailyHabits = state.habits.filter(h => h.frequency === 'daily');
  const dailyTotal  = dailyHabits.length;
  // We approximate today's completions by counting dailies with streak > 0
  // (a streak > 0 means the current period is completed)
  const todayCount  = dailyHabits.filter(h => (h.streak || 0) > 0).length;
  document.getElementById('today-text').textContent      = `${todayCount} / ${dailyTotal}`;
  const todayPct = dailyTotal > 0 ? Math.min(100, (todayCount / dailyTotal) * 100) : 0;
  document.getElementById('today-bar-fill').style.width  = `${todayPct}%`;

  // Used frequencies
  const usedFreqs = [...new Set(state.habits.map(h => h.frequency))];

  // Achievements
  setAchievement('ach-first-step',   total_completions >= 1);
  setAchievement('ach-week-warrior', bestStreak >= 7);
  setAchievement('ach-habit-master', state.habits.length >= 10);
  setAchievement('ach-consistent',   bestStreak >= 30);
  setAchievement('ach-explorer',     ['daily', 'weekly', 'monthly'].every(f => usedFreqs.includes(f)));
  setAchievement('ach-legend',       total_completions >= 100);
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
  cb.checked = !!habit.completed;
  cb.addEventListener('change', handleHabitCheck);

  const nameContainer = document.createElement('span');
  nameContainer.className = 'habit-name-container';

  const nameSpan = document.createElement('span');
  nameSpan.className   = 'habit-name';
  nameSpan.textContent = habit.name;
  nameSpan.title       = habit.name;
  nameContainer.appendChild(nameSpan);

  if (habit.description) {
    const descSpan = document.createElement('span');
    descSpan.className   = 'habit-desc';
    descSpan.textContent = habit.description;
    descSpan.title       = habit.description;
    nameContainer.appendChild(descSpan);
  }

  label.append(cb, nameContainer);

  // Streak badge
  if (habit.streak && habit.streak > 0) {
    const streakEl = document.createElement('span');
    streakEl.className   = 'streak-badge';
    streakEl.textContent = `\u{1F525}${habit.streak}`;
    li.appendChild(label);
    li.appendChild(streakEl);
  } else {
    li.appendChild(label);
  }

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
  del.textContent = '\u00d7';
  del.title       = 'Delete habit';
  del.addEventListener('click', handleDeleteHabit);

  li.append(diffEl, xpEl, del);
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

    if (result.completed) {
      const totalXp = result.xp_reward + (result.streak_bonus_xp || 0);
      showXpToast(result.xp_reward, result.streak_bonus_xp);
      showFeedback(`"${habit.name}" completed! +${totalXp} XP`, 'success');
    } else {
      showFeedback(`"${habit.name}" unmarked.`, 'success');
    }

    // Update profile from response
    if (result.level_info) {
      state.profile = {
        ...state.profile,
        total_xp: result.level_info.total_xp,
        level_info: result.level_info,
      };
      if (result.completed) {
        state.profile.total_completions = (state.profile.total_completions || 0) + 1;
      } else {
        state.profile.total_completions = Math.max(0, (state.profile.total_completions || 0) - 1);
      }
    }

    // Update completion and streak on the habit in state
    habit.completed = !!result.completed;
    if (result.streak !== undefined) {
      habit.streak = result.streak;
    }

    renderAllLists();
    renderGamification();
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

  const description  = document.getElementById('habit-desc-input').value.trim();

  try {
    await apiPost('/createTask', {
      name,
      description,
      frequency:   state.selectedFrequency,
    });
    state.habits = await apiFetchHabits();
    state.profile = await apiFetchProfile();
    renderAllLists();
    renderGamification();
    showFeedback(`"${name}" added as ${state.selectedFrequency} habit!`, 'success');
    document.getElementById('habit-name-input').value = '';
    document.getElementById('habit-desc-input').value = '';
    updateHabitButtons();
    hideRecurringConfig();
  } catch (err) {
    showFeedback(err.message || 'Failed to add habit.', 'error');
  }
}

async function handleTrackNow() {
  const input = document.getElementById('habit-name-input');
  const name  = input.value.trim();
  if (!name) { showFeedback('Please enter a habit name.', 'error'); input.focus(); return; }
  showOneTimeConfig();
}

async function handleConfirmOneTime() {
  const name        = document.getElementById('habit-name-input').value.trim();
  const description = document.getElementById('habit-desc-input').value.trim();

  if (!name) { showFeedback('Please enter a habit name.', 'error'); return; }

  try {
    const result = await apiPost('/trackOneTime', { name, description });
    showXpToast(result.xp_reward);
    showFeedback(`"${name}" tracked! +${result.xp_reward} XP`, 'success');

    // Update profile
    if (result.level_info) {
      state.profile = {
        ...state.profile,
        total_xp: result.level_info.total_xp,
        level_info: result.level_info,
        total_completions: (state.profile?.total_completions || 0) + 1,
      };
    }

    renderGamification();
    document.getElementById('habit-name-input').value = '';
    document.getElementById('habit-desc-input').value = '';
    updateHabitButtons();
    hideOneTimeConfig();
  } catch (err) {
    showFeedback(err.message || 'Failed to track one-time habit.', 'error');
  }
}

// ─── Recurring Config UI ──────────────────────────────────────────────────────
function showRecurringConfig() {
  hideOneTimeConfig();
  document.getElementById('recurring-config').classList.remove('hidden');
  document.querySelectorAll('.freq-btn').forEach(b => b.classList.remove('active'));
  state.selectedFrequency  = null;
}

function hideRecurringConfig() {
  document.getElementById('recurring-config').classList.add('hidden');
  state.selectedFrequency  = null;
}

// ─── One-Time Config UI ──────────────────────────────────────────────────────
function showOneTimeConfig() {
  hideRecurringConfig();
  document.getElementById('one-time-config').classList.remove('hidden');
}

function hideOneTimeConfig() {
  document.getElementById('one-time-config').classList.add('hidden');
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
  if (busy) {
    document.getElementById('btn-login').disabled    = true;
    document.getElementById('btn-register').disabled = true;
  } else {
    updateLoginButtons();
  }
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
  document.getElementById('header-username').textContent = state.username || '';

  try {
    const [habits, profile] = await Promise.all([apiFetchHabits(), apiFetchProfile()]);
    state.habits  = habits;
    state.profile = profile;
  } catch {
    state.habits  = [];
    state.profile = { total_xp: 0, total_completions: 0, level_info: { level: 1, title: 'Beginner', xp_in_level: 0, xp_needed: 100, total_xp: 0 } };
  }

  renderAllLists();
  renderGamification();
}

// ─── Button State Helpers ─────────────────────────────────────────────────────
function updateLoginButtons() {
  const hasUser = document.getElementById('login-username').value.trim().length > 0;
  const hasPass = document.getElementById('login-password').value.length > 0;
  const enabled = hasUser && hasPass;
  document.getElementById('btn-login').disabled = !enabled;
  document.getElementById('btn-register').disabled = !enabled;
}

function updateHabitButtons() {
  const hasName = document.getElementById('habit-name-input').value.trim().length > 0;
  document.getElementById('btn-track-now').disabled = !hasName;
  document.getElementById('btn-add-recurring').disabled = !hasName;
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
  document.getElementById('login-username').addEventListener('input', updateLoginButtons);
  document.getElementById('login-password').addEventListener('input', updateLoginButtons);
  updateLoginButtons();

  // Logout
  document.getElementById('btn-logout').addEventListener('click', () => {
    clearAuth();
    state.habits  = [];
    state.profile = null;
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

  // One-time config
  document.getElementById('btn-confirm-onetime').addEventListener('click', handleConfirmOneTime);
  document.getElementById('btn-cancel-onetime').addEventListener('click', () => {
    hideOneTimeConfig();
  });

  // Frequency selection
  document.querySelectorAll('.freq-btn').forEach(btn =>
    btn.addEventListener('click', () => {
      document.querySelectorAll('.freq-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.selectedFrequency = btn.dataset.freq;
    })
  );

  // Habit name validation
  document.getElementById('habit-name-input').addEventListener('input', updateHabitButtons);
  updateHabitButtons();

  // Enter key in habit input
  document.getElementById('habit-name-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') handleTrackNow();
  });
}

document.addEventListener('DOMContentLoaded', initApp);
