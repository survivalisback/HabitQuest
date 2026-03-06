const API_BASE = 'http://localhost:8000';
const STORAGE_KEY_HABITS = 'habitquest_habits';
const STORAGE_KEY_COMPLETIONS = 'habitquest_completions';

const state = {
  habits: [],
  completions: [],
  selectedFrequency: null,
};

function saveHabits() {
  try {
    localStorage.setItem(STORAGE_KEY_HABITS, JSON.stringify(state.habits));
  } catch (e) {
    console.warn('localStorage unavailable — habits not persisted:', e);
  }
}

function loadHabits() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_HABITS);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.warn('Failed to load habits from localStorage:', e);
    return [];
  }
}

function saveCompletions() {
  try {
    localStorage.setItem(STORAGE_KEY_COMPLETIONS, JSON.stringify(state.completions));
  } catch (e) {
    console.warn('localStorage unavailable — completions not persisted:', e);
  }
}

function loadCompletions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_COMPLETIONS);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.warn('Failed to load completions from localStorage:', e);
    return [];
  }
}

function getPeriodKey(frequency, date) {
  const d = date || new Date();

  if (frequency === 'daily') {
    return d.toISOString().slice(0, 10);
  }

  if (frequency === 'weekly') {
    const jan1 = new Date(d.getFullYear(), 0, 1);
    const dayOfYear = Math.floor((d - jan1) / 86400000) + 1;
    const dow = d.getDay() === 0 ? 7 : d.getDay();
    const weekNum = Math.ceil((dayOfYear + jan1.getDay() - 1) / 7);
    const year = d.getFullYear();
    const ww = String(weekNum).padStart(2, '0');
    return `${year}-W${ww}`;
  }

  if (frequency === 'monthly') {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    return `${y}-${m}`;
  }

  return d.toISOString();
}

function isHabitCompletedThisPeriod(habit) {
  const currentKey = getPeriodKey(habit.frequency);
  return state.completions.some(
    (c) => c.habitId === habit.id && getPeriodKey(c.frequency, new Date(c.completedAt)) === currentKey
  );
}

function pruneStaleCompletions() {
  state.completions = state.completions.filter((c) => {
    if (c.oneTime) return true;
    const currentKey = getPeriodKey(c.frequency);
    const completionKey = getPeriodKey(c.frequency, new Date(c.completedAt));
    return completionKey === currentKey;
  });
  saveCompletions();
}

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

async function apiCreateTask(habit) {
  try {
    const res = await fetch(`${API_BASE}/createTask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: habit.name,
        description: '',
        frequency: habit.frequency,
      }),
    });
    if (!res.ok) {
      console.warn(`createTask responded with ${res.status}`);
    }
  } catch (e) {
    console.warn('createTask: backend unreachable —', e.message);
  }
}

async function apiTrackHabit(data) {
  try {
    const res = await fetch(`${API_BASE}/trackHabit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: data.name,
        frequency: data.frequency,
        completed_at: data.completedAt,
      }),
    });
    if (!res.ok && res.status !== 404) {
      console.warn(`trackHabit responded with ${res.status}`);
    }
  } catch (e) {
    console.warn('trackHabit: backend unreachable —', e.message);
  }
}

let feedbackTimer = null;

function showFeedback(msg, type = 'success') {
  const banner = document.getElementById('feedback-banner');
  banner.textContent = msg;
  banner.className = type; // 'success' or 'error'
  banner.classList.remove('hidden');

  if (feedbackTimer) clearTimeout(feedbackTimer);
  feedbackTimer = setTimeout(() => {
    banner.classList.add('hidden');
  }, 3000);
}

function showFrequencyPicker() {
  document.getElementById('frequency-picker').classList.remove('hidden');
  document.querySelectorAll('.freq-btn').forEach((b) => b.classList.remove('active'));
  state.selectedFrequency = null;
}

function hideFrequencyPicker() {
  document.getElementById('frequency-picker').classList.add('hidden');
  state.selectedFrequency = null;
}

function createHabitListItem(habit) {
  const li = document.createElement('li');
  li.className = 'habit-item';
  li.dataset.id = habit.id;
  li.dataset.frequency = habit.frequency;

  const completed = isHabitCompletedThisPeriod(habit);

  const label = document.createElement('label');

  const checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.checked = completed;
  checkbox.disabled = completed;
  checkbox.addEventListener('change', handleHabitCheck);

  const nameSpan = document.createElement('span');
  nameSpan.className = 'habit-name';
  nameSpan.textContent = habit.name;
  nameSpan.title = habit.name;

  label.appendChild(checkbox);
  label.appendChild(nameSpan);

  const badge = document.createElement('span');
  badge.className = `freq-badge ${habit.frequency}`;
  badge.textContent = habit.frequency.charAt(0).toUpperCase() + habit.frequency.slice(1);

  const deleteBtn = document.createElement('button');
  deleteBtn.className = 'btn-delete-habit';
  deleteBtn.textContent = '×';
  deleteBtn.title = 'Delete habit';
  deleteBtn.addEventListener('click', handleDeleteHabit);

  li.appendChild(label);
  li.appendChild(badge);
  li.appendChild(deleteBtn);

  return li;
}

function renderList(freq) {
  const ul = document.getElementById(`list-${freq}`);
  const emptyEl = document.getElementById(`empty-${freq}`);

  const habitsForFreq = state.habits.filter((h) => h.frequency === freq);
  const incomplete = habitsForFreq.filter((h) => !isHabitCompletedThisPeriod(h));

  ul.innerHTML = '';

  if (habitsForFreq.length === 0) {
    emptyEl.textContent = `No ${freq} habits yet.`;
    emptyEl.classList.remove('hidden');
    return;
  }

  if (incomplete.length === 0) {
    emptyEl.textContent = 'All done! ✓';
    emptyEl.classList.remove('hidden');
    return;
  }

  emptyEl.classList.add('hidden');

  incomplete.forEach((habit) => {
    ul.appendChild(createHabitListItem(habit));
  });
}

function renderAllLists() {
  renderList('daily');
  renderList('weekly');
  renderList('monthly');
}

function handleTrackNow() {
  const input = document.getElementById('habit-name-input');
  const name = input.value.trim();

  if (!name) {
    showFeedback('Please enter a habit name.', 'error');
    input.focus();
    return;
  }

  const completedAt = new Date().toISOString();
  apiTrackHabit({ name, frequency: 'once', completedAt }).then(() => {}).catch(() => {});

  showFeedback(`"${name}" tracked! (saved locally)`, 'success');
  input.value = '';
  hideFrequencyPicker();
}

function handleAddRecurring() {
  const input = document.getElementById('habit-name-input');
  const name = input.value.trim();

  if (!name) {
    showFeedback('Please enter a habit name.', 'error');
    input.focus();
    return;
  }

  if (!state.selectedFrequency) {
    showFrequencyPicker();
    return;
  }

  const habit = {
    id: generateId(),
    name,
    frequency: state.selectedFrequency,
    createdAt: new Date().toISOString(),
  };

  state.habits.push(habit);
  saveHabits();

  apiCreateTask(habit).then(() => {}).catch(() => {});

  showFeedback(`"${name}" added as ${state.selectedFrequency} habit!`, 'success');
  input.value = '';
  hideFrequencyPicker();
  renderAllLists();
}

function handleFrequencySelect(e) {
  const btn = e.currentTarget;
  const freq = btn.dataset.freq;

  document.querySelectorAll('.freq-btn').forEach((b) => b.classList.remove('active'));
  btn.classList.add('active');

  state.selectedFrequency = freq;
  handleAddRecurring();
}

function handleHabitCheck(e) {
  const checkbox = e.target;
  checkbox.disabled = true;

  const li = checkbox.closest('.habit-item');
  const habitId = li.dataset.id;
  const habit = state.habits.find((h) => h.id === habitId);
  if (!habit) return;

  const completedAt = new Date().toISOString();
  const completion = {
    habitId: habit.id,
    habitName: habit.name,
    frequency: habit.frequency,
    completedAt,
    oneTime: false,
  };

  state.completions.push(completion);
  saveCompletions();

  apiTrackHabit({ name: habit.name, frequency: habit.frequency, completedAt })
    .then(() => {})
    .catch(() => {});

  li.classList.add('completing');
  setTimeout(() => {
    renderList(habit.frequency);
  }, 500);
}

function handleDeleteHabit(e) {
  const li = e.currentTarget.closest('.habit-item');
  const habitId = li.dataset.id;
  const freq = li.dataset.frequency;

  state.habits = state.habits.filter((h) => h.id !== habitId);
  state.completions = state.completions.filter((c) => c.habitId !== habitId);

  saveHabits();
  saveCompletions();
  renderList(freq);
}

function initApp() {
  state.habits = loadHabits();
  state.completions = loadCompletions();
  pruneStaleCompletions();

  renderAllLists();

  document.getElementById('btn-track-now').addEventListener('click', handleTrackNow);
  document.getElementById('btn-add-recurring').addEventListener('click', handleAddRecurring);
  document.getElementById('btn-cancel-freq').addEventListener('click', hideFrequencyPicker);

  document.querySelectorAll('.freq-btn').forEach((btn) => {
    btn.addEventListener('click', handleFrequencySelect);
  });

  document.getElementById('habit-name-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      if (document.getElementById('frequency-picker').classList.contains('hidden')) {
        handleTrackNow();
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', initApp);
