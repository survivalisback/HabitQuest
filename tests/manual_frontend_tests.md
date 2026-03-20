# HabitQuest — Manual Frontend Test Script

> **Prerequisites**
>
> - Backend running on `http://localhost:8000`
> - Open `index.html` (or the served frontend) in a modern browser
> - Browser DevTools open (Console + Network tabs) for observing errors and requests
> - Start each section from a **clean state** unless noted otherwise:
>   clear `localStorage` keys `habitquest_token` and `habitquest_username`, then reload

---

## 1  Authentication — Login

### 1.1  Empty form submission

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Load the app with no stored session | Login overlay is visible, covering the entire screen. "HabitQuest" title and tagline "Track habits. Earn XP. Level up." are shown. |
| 2 | Leave both fields empty, observe buttons | Both "Sign in" and "Create account" buttons are **disabled** (grayed out, `opacity: 0.5`, not clickable). |
| 3 | Type a username but leave password empty | Buttons remain disabled. |
| 4 | Clear username, type only a password | Buttons remain disabled. |

### 1.2  Login with invalid credentials

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter username `nonexistent_user_xyz` and password `wrong` | Both buttons become enabled. |
| 2 | Click "Sign in" | A **red error banner** appears below the form with a message like *"Invalid username or password."* (the `detail` from the API 400/401 response). The login overlay stays visible. Both input fields retain their values. |

### 1.3  Login with wrong password for existing user

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Register a user first (see section 2) — e.g. `testuser` / `pass1234` | — |
| 2 | Sign out, then enter `testuser` and password `wrongpassword` | — |
| 3 | Click "Sign in" | Red error banner: *"Invalid username or password."* Login overlay remains. Inputs not cleared. |

### 1.4  Successful login

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter valid credentials (`testuser` / `pass1234`) | — |
| 2 | Click "Sign in" | Login overlay **disappears**. Main app appears with the header showing the username on the right and a "Sign out" button. The habit panel and gamification panel load. |
| 3 | Check `localStorage` | Keys `habitquest_token` and `habitquest_username` are set. |

### 1.5  Keyboard navigation on login form

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Focus the username field, type `testuser`, press **Enter** | Focus moves to the **password** field. No form submission yet. |
| 2 | Type `pass1234`, press **Enter** | Login is triggered (equivalent to clicking "Sign in"). On success the overlay disappears. |

### 1.6  Session persistence across reloads

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Log in successfully | Main app visible. |
| 2 | Reload the page (F5) | Login overlay does **not** appear. App loads directly into the main view with the same username in the header. Habits and profile data load from the API. |

---

## 2  Authentication — Registration

### 2.1  Register a new account

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | On the login overlay, enter `newuser123` and password `abcd1234` | Both buttons are enabled. |
| 2 | Click "Create account" | Login overlay disappears. Main app loads. Header shows `newuser123`. `localStorage` has the token. This is a fresh account so: level 1, 0 XP, 0 completions, title "Beginner", no habits in any list. |

### 2.2  Register with short password

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter username `shortpw` and password `ab` (2 chars) | — |
| 2 | Click "Create account" | Red error banner: *"Password must be at least 4 characters."* The overlay stays open. |

### 2.3  Register with duplicate username

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Register `dupuser` / `pass1234` and sign out | — |
| 2 | Enter `dupuser` / `otherpass` | — |
| 3 | Click "Create account" | Red error banner: *"Username already exists."* Overlay remains. |

### 2.4  Register with whitespace-only username

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Enter `   ` (spaces only) as username and `pass1234` as password | Buttons may become enabled because fields are non-empty. |
| 2 | Click "Create account" | Red error banner: *"Username is required."* (backend strips whitespace and rejects). |

---

## 3  Sign Out

### 3.1  Basic sign-out flow

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Log in successfully | Main app visible. |
| 2 | Click "Sign out" in the header | Login overlay reappears. Main app is hidden. |
| 3 | Check `localStorage` | `habitquest_token` and `habitquest_username` are **cleared**. |
| 4 | Reload the page | Login overlay is shown (no auto-login). |

---

## 4  Habit Creation — Recurring Habits

### 4.1  Input validation — empty name

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Leave the habit name field empty | "Track Now" and "Add Recurring" buttons are **disabled**. |
| 2 | Type a space and delete it (field goes back to empty) | Buttons stay disabled. |

### 4.2  Add a daily habit

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type `Morning run` in the habit name field | Both "Track Now" and "Add Recurring" buttons become enabled. |
| 2 | Optionally type `Run 3km before breakfast` in the description textarea | — |
| 3 | Click "Add Recurring" | A **recurring config panel** appears with a blue-tinted background. It shows a "FREQUENCY" label and three pill buttons: **Daily**, **Weekly**, **Monthly**. Also a "Confirm" and "Cancel" button. |
| 4 | Click the "Daily" pill | The Daily pill gets a **blue filled background** with white text. The other pills remain gray/outlined. |
| 5 | Click "Confirm" | The config panel disappears. A **green feedback banner** appears: *`"Morning run" added!`*. The habit name and description inputs are **cleared**. Under the **Daily** section of the habit list, `Morning run` now appears with: an unchecked checkbox, the name, description (if entered), difficulty dots (likely 3 filled out of 5 from AI/static evaluation), an XP chip (e.g. `+30 XP`), and a delete button (×). |

### 4.3  Add a weekly habit

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type `Grocery shopping`, click "Add Recurring" | Recurring config panel opens. |
| 2 | Click "Weekly", then "Confirm" | Habit appears under the **Weekly** section with a purple left border accent. Feedback banner confirms. |

### 4.4  Add a monthly habit

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type `Budget review`, click "Add Recurring" | Config panel opens. |
| 2 | Click "Monthly", then "Confirm" | Habit appears under the **Monthly** section with a cyan left border accent. |

### 4.5  Cancel recurring config

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type `Cancelled habit`, click "Add Recurring" | Config panel opens. |
| 2 | Click "Cancel" | Config panel disappears. The input fields are **not** cleared (the name `Cancelled habit` remains). No habit is created. No feedback banner. |

### 4.6  Empty state messages

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Log in to a fresh account with no habits | Under each frequency section (Daily, Weekly, Monthly), the text *"No daily habits yet."*, *"No weekly habits yet."*, and *"No monthly habits yet."* is shown in gray italic. |
| 2 | Add one daily habit | The "No daily habits yet." message disappears, replaced by the habit item. Weekly and monthly still show their empty messages. |

---

## 5  Habit Completion — Toggling

### 5.1  Complete a daily habit

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Ensure a daily habit exists (e.g. `Morning run`, +30 XP) | Habit shows with an **unchecked** checkbox. |
| 2 | Click the checkbox | The checkbox becomes **disabled** briefly (during the API call). Then it becomes **checked** with a **blue filled background and white checkmark**. A **green feedback banner** appears: *`"Morning run" completed! +30 XP`*. An **XP toast** slides in from the bottom-right corner showing `+30 XP`. |
| 3 | Observe the gamification panel | The XP bar updates (e.g. 30/100 XP). "Total Done" stat increments by 1. "Today's Progress" bar may update. The level and title update if a level-up threshold is crossed. |
| 4 | Wait ~2 seconds | The XP toast fades out. |
| 5 | Wait ~3.2 seconds | The feedback banner disappears. |

### 5.2  Uncomplete a habit (toggle off)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click the already-checked checkbox for `Morning run` | Checkbox becomes **unchecked** (back to border-only styling). No XP toast appears. The feedback banner should indicate the habit was uncompleted or simply not show a toast. |
| 2 | Observe the gamification panel | XP reverts (decreases by 30). "Total Done" decrements by 1. XP bar width shrinks accordingly. |

### 5.3  Completion with streak bonus

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Have a daily habit that has been completed on at least 3 consecutive days (may need to use the API directly or wait for real days) | The habit item shows a 🔥 streak badge (e.g. `🔥3`). |
| 2 | Complete the habit today | XP toast shows the bonus: e.g. `+30 XP (+3 streak bonus)`. The feedback banner also mentions the completion. Total XP updates by base + bonus. |

### 5.4  Streak badge visibility

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Observe a habit with streak = 0 | **No** 🔥 badge is shown next to the habit name. |
| 2 | Observe a habit with streak > 0 | A small orange pill `🔥{count}` appears next to the habit name. |

### 5.5  Toggle failure (network error)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Stop the backend server | — |
| 2 | Click a habit checkbox | The checkbox briefly disables, then **reverts** to its previous state (checked or unchecked). A **red error feedback banner** appears with an error message. No XP toast. |
| 3 | Restart the server | Subsequent toggles work normally. |

---

## 6  Habit Deletion

### 6.1  Delete a habit that is not completed

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Ensure a daily habit exists and its checkbox is **unchecked** | — |
| 2 | Click the **×** (delete) button on the habit | The habit is removed from the list. A feedback banner confirms deletion. The XP and Total Done stats do **not** change (no XP was earned from this uncompleted habit). |

### 6.2  Delete a completed habit

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Complete a habit (checkbox checked, XP earned) | Note the current total XP (e.g. 30). |
| 2 | Click the **×** delete button on the completed habit | The habit is removed. XP is **reverted** (total XP decreases back, e.g. from 30 to 0). Total Done also decrements. The gamification panel updates. |

### 6.3  Delete the last habit in a frequency group

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Have exactly one daily habit | — |
| 2 | Delete it | The daily section now shows *"No daily habits yet."* in gray italic. |

---

## 7  One-Time Habit Tracking

### 7.1  Track a one-time habit

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type `Clean the garage` in the habit name field | "Track Now" and "Add Recurring" become enabled. |
| 2 | Click "Track Now" | A **one-time config panel** appears with a green-tinted background. It shows "Track It" (green) and "Cancel" buttons. |
| 3 | Click "Track It" | Config panel disappears. **Green feedback banner**: *`"Clean the garage" tracked! +{xp} XP`*. **XP toast** appears with the reward. The input fields are cleared. |
| 4 | Check the habit lists | The one-time habit does **not** appear in any frequency list (daily/weekly/monthly). It is not a recurring habit. |
| 5 | Check gamification panel | Total XP increases by the awarded amount. Total Done increments by 1. Level/XP bar update if threshold crossed. |

### 7.2  Cancel one-time tracking

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Type `Temp task`, click "Track Now" | Config panel opens. |
| 2 | Click "Cancel" | Config panel closes. Input not cleared. No habit tracked. No XP change. |

---

## 8  Gamification Panel

### 8.1  Level badge and title

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Log in to a fresh account | Level badge shows **LVL 1**. Title shows **"Beginner"**. XP bar shows `0 / 100 XP` with 0% fill. |
| 2 | Earn 100+ XP (complete habits or track one-time habits) | Level badge updates to **LVL 2**. Title remains "Beginner" (title changes at level 3). XP bar resets for the new level (shows progress toward next threshold, e.g. `0 / 200 XP`). |

### 8.2  XP bar accuracy

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | At level 1, earn 50 XP | XP bar shows `50 / 100 XP`. Bar fill is 50% width. |
| 2 | Earn 30 more XP (total 80) | Bar shows `80 / 100 XP`. Fill is 80%. |
| 3 | XP bar never exceeds 100% | If somehow `xp_in_level > xp_needed`, bar is capped at 100% width. |

### 8.3  XP bar animation

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Complete a habit | The XP bar fill width animates smoothly over ~0.7 seconds (CSS transition with `cubic-bezier`) from the old width to the new width. It does not jump instantly. |

### 8.4  Stats cards

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Fresh account | "Day Streak" shows `0`. "Total Done" shows `0`. |
| 2 | Complete one daily habit | "Total Done" shows `1`. "Day Streak" may show `1` if the streak updates. |

### 8.5  Today's progress bar

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Have 4 daily habits, none completed | "Today's Progress" shows `0 / 4`. Bar is at 0%. |
| 2 | Complete 2 of them | Shows `2 / 4`. Bar is at 50%. |
| 3 | Complete all 4 | Shows `4 / 4`. Bar is at 100%. |
| 4 | Have no daily habits at all | Bar shows `0 / 0` or similar. Progress bar is at 0% (not NaN or broken). |

---

## 9  Achievements

### 9.1  Locked achievements

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Fresh account, 0 completions | All 6 achievement badges are shown in **grayscale** at ~35% opacity with gray borders. Each shows its icon and name but is visually "locked". |

### 9.2  Unlock "First Step" (1 completion)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Complete any habit or track a one-time habit | The **"First Step" (⭐)** achievement unlocks: it gains a gold/orange glowing border, full opacity, and color. The other 5 remain locked. |

### 9.3  Unlock "Explorer" (use all frequencies)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create and have at least one daily, one weekly, and one monthly habit | The **"Explorer" (🗺️)** achievement unlocks. |

### 9.4  Achievement hover effect

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Hover over an **unlocked** achievement | The badge lifts slightly (translateY -2px) with a smooth transition. |
| 2 | Hover over a **locked** achievement | No lift effect (or minimal). |

---

## 10  Difficulty and XP Display

### 10.1  Difficulty dots

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create a habit (the backend/AI assigns difficulty) | The habit item shows **5 dots**. The number of filled (solid) dots corresponds to the assigned difficulty (1-5). Unfilled dots are hollow/gray. |
| 2 | Create multiple habits | Each may have a different number of filled dots depending on the AI/static evaluation. |

### 10.2  XP chip display

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create a daily habit with difficulty 3 | XP chip shows `+30 XP` (or the AI-evaluated amount). |
| 2 | Create a weekly habit with difficulty 3 | XP chip shows `+45 XP` (1.5× multiplier). |
| 3 | Create a monthly habit with difficulty 3 | XP chip shows `+60 XP` (2× multiplier). |

---

## 11  Feedback Banner Behavior

### 11.1  Auto-dismiss timing

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Trigger any success action (add/complete/delete a habit) | Green feedback banner appears. |
| 2 | Wait ~3.2 seconds without interacting | The banner **auto-dismisses** (disappears). |

### 11.2  Successive feedback messages

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Complete habit A | Green banner: *`"A" completed! +30 XP`* |
| 2 | Immediately complete habit B (before banner A disappears) | Banner **replaces** with: *`"B" completed! +45 XP`*. The timer resets. |

### 11.3  Error feedback banner

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Trigger an error (e.g. stop backend, try to complete a habit) | A **red** feedback banner appears with a red left border and light red background. It contains the error message. |

---

## 12  XP Toast Behavior

### 12.1  Toast animation

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Complete a habit | An XP toast slides up from the bottom-right corner. It's a rounded pill with an orange/amber gradient background and bold white text (e.g. `+30 XP`). |
| 2 | Observe the entrance | The toast scales from 0.9 to 1.0 and moves up, taking ~0.3 seconds. |
| 3 | Wait ~2 seconds | The toast begins to fade out and collapse, taking ~0.6 seconds. |
| 4 | After fade-out | The toast element is removed from the DOM. |

### 12.2  Toast with streak bonus text

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Complete a habit that has a streak ≥ 3 | Toast shows: `+30 XP (+3 streak bonus)` (amounts vary). |

### 12.3  Multiple toasts stacking

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Rapidly complete two habits | Two toasts appear stacked vertically in the bottom-right corner (newest on bottom due to `column-reverse` flex direction). Both fade independently. |

---

## 13  Responsive Layout

### 13.1  Desktop layout (> 820px)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | View at ≥ 900px width | Two-column layout: habit panel on the left, gamification panel on the right. The gamification panel is sticky (stays visible when scrolling). |

### 13.2  Mobile layout (≤ 820px)

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Resize browser to ≤ 820px or use mobile emulation | Layout switches to **single column**. Habit panel stacks above the gamification panel. The gamification panel is no longer sticky. |

### 13.3  Login overlay responsiveness

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | View login at narrow width | The login card remains centered and readable. Fields and buttons don't overflow. |

---

## 14  Session Expiration

### 14.1  Expired token handling

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Log in, then manually change `habitquest_token` in `localStorage` to `expired-garbage` | — |
| 2 | Reload the page | The API calls fail with 401. The app **clears** `localStorage` auth data and shows the **login overlay**. |

### 14.2  Token expiration during use

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Log in, then wait for the token to expire (default 24h — or temporarily set `jwt_expires_in_seconds` to a small value on the backend) | — |
| 2 | Try to complete a habit | The API returns 401. A red error banner says *"Session expired."* The login overlay appears. |

---

## 15  Edge Cases and Visual Bugs

### 15.1  Very long habit name

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create a habit with a very long name (e.g. 200 characters) | The name is **truncated with ellipsis** (`text-overflow: ellipsis`) in the habit list. It does not overflow or break the layout. The XP chip and delete button remain visible and aligned. |

### 15.2  Very long description

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create a habit with a very long description | The description is truncated with ellipsis. It does not push other elements out of alignment. |

### 15.3  Special characters in habit name

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create a habit named `<script>alert("XSS")</script>` | The name is rendered as **plain text**, not executed as HTML. No alert dialog appears. The text shows literally in the habit list. |

### 15.4  Many habits in one category

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Create 20+ daily habits | All habits render in a scrollable list. Performance remains smooth. No layout breakage. |

### 15.5  Level-up visual update

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Be at 90/100 XP (level 1, close to level 2) | XP bar at 90%. |
| 2 | Complete a habit worth 30 XP | Level badge changes from **LVL 1** to **LVL 2**. XP bar resets to show progress in the new level (e.g. `20 / 200 XP` at 10%). Title updates if the new level crosses a title milestone. |

### 15.6  Zero XP bar when exactly leveling up

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Be at exactly 0 XP in a new level | XP bar shows `0 / {needed} XP` with 0% fill (no visual artifact, bar doesn't show a sliver). |

### 15.7  Rapid toggling

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Click a habit checkbox, then immediately click it again while the first request is in-flight | The checkbox is **disabled** during the first request, so the second click is ignored. The state resolves correctly after the first request completes. No double XP award or inconsistent state. |

### 15.8  Helper text for description

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Observe the description textarea | A helper text is visible: *"helps AI determine XP"* (or similar), guiding the user to add a description for better AI evaluation. |

---

## 16  Browser Console Checks

### 16.1  No JavaScript errors on load

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open DevTools Console, reload the page (logged in) | **No** red JavaScript errors in the console. Network requests to the API all return 200. |

### 16.2  No errors during normal flow

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Perform a full flow: login → add habit → complete → delete → sign out | Console shows no uncaught exceptions or errors. All API calls succeed (visible in Network tab). |

### 16.3  API request format

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Open Network tab, create a habit | The POST request to the backend includes the auth token (in the body or header). The request body is JSON with `name`, `description`, `frequency`. |
| 2 | Toggle a habit | The request includes `habit_id` and the auth token. |

---

## Summary Checklist

| Area | # Tests | Key Risks Covered |
|------|---------|-------------------|
| Login | 6 | Empty form, bad creds, keyboard nav, session persistence |
| Registration | 4 | New account, short password, duplicate, whitespace |
| Sign out | 1 | Clears session, shows login |
| Habit creation | 6 | Validation, all frequencies, cancel, empty states |
| Habit completion | 5 | Toggle on/off, XP update, streak bonus, failure revert |
| Habit deletion | 3 | Uncompleted, completed (XP revert), last habit |
| One-time tracking | 2 | Track + cancel |
| Gamification panel | 5 | Level, XP bar, stats, today's progress |
| Achievements | 3 | Locked state, unlock, hover |
| Difficulty/XP display | 2 | Dots, chip values |
| Feedback banner | 3 | Auto-dismiss, replace, error variant |
| XP toast | 3 | Animation, streak text, stacking |
| Responsive layout | 3 | Desktop, mobile, login |
| Session expiration | 2 | Corrupted token, expired token |
| Edge cases | 8 | Long text, XSS, many habits, level-up, rapid toggle |
| Console checks | 3 | No errors on load, during flow, request format |

**Total: ~59 manual test scenarios**
