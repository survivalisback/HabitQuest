# HabitQuest User Guide

Welcome to **HabitQuest** — a gamified habit tracker that turns your daily routines into an adventure. Build habits, earn XP, level up, unlock achievements, and watch your progress grow over time.

This guide walks you through every feature of the application.

---

## Table of Contents

1. [Getting Started](#getting-started)
   - [Creating an Account](#creating-an-account)
   - [Signing In](#signing-in)
   - [Signing Out](#signing-out)
2. [The Dashboard](#the-dashboard)
   - [Overview](#overview)
   - [Left Panel — Habit Management](#left-panel--habit-management)
   - [Right Panel — Your Progress](#right-panel--your-progress)
3. [Managing Habits](#managing-habits)
   - [Creating a Recurring Habit](#creating-a-recurring-habit)
   - [Logging a One-Time Achievement](#logging-a-one-time-achievement)
   - [Editing a Habit](#editing-a-habit)
   - [Deleting a Habit](#deleting-a-habit)
4. [Completing Habits](#completing-habits)
   - [Marking a Habit as Complete](#marking-a-habit-as-complete)
   - [Undoing a Completion](#undoing-a-completion)
5. [Experience Points (XP)](#experience-points-xp)
   - [How XP is Calculated](#how-xp-is-calculated)
   - [Frequency Multipliers](#frequency-multipliers)
   - [AI-Powered XP (Optional)](#ai-powered-xp-optional)
6. [Streaks](#streaks)
   - [How Streaks Work](#how-streaks-work)
   - [Streak Bonus XP](#streak-bonus-xp)
7. [Levels and Titles](#levels-and-titles)
8. [Achievements](#achievements)
9. [Statistics and Today's Progress](#statistics-and-todays-progress)
10. [Tips and Tricks](#tips-and-tricks)

---

## Getting Started

### Creating an Account

When you first open HabitQuest, you will see the sign-in screen.

![login](/docs/images/login.png)

To create a new account:

1. Enter a **username** of your choice.
2. Enter a **password** (must be at least 4 characters).
3. Click the **Register** button.

Your account is created and you are signed in automatically.

### Signing In

If you already have an account:

1. Enter your **username**.
2. Enter your **password**.
3. Click the **Sign In** button.

Your session is remembered, so you will stay signed in even if you close and reopen the page.

### Signing Out

To sign out, click the **Sign out** button in the top-right corner of the screen, next to your username. This will end your session and return you to the sign-in screen.

![header](/docs/images/header.png)

---

## The Dashboard

### Overview

After signing in, you arrive at the main dashboard. It is divided into two panels:

![overview](/docs/images/overview.png)

| Area | Purpose |
|------|---------|
| **Left panel** | Create, view, and manage your habits |
| **Right panel** | View your level, XP, streaks, achievements, and daily progress |

On smaller screens (mobile or tablet), these panels stack vertically instead of side by side.

### Left Panel — Habit Management

The left side of the dashboard contains:

- **Habit input area** — where you create new habits or log one-time achievements.
- **Daily Habits** — a list of all your daily habits, shown with a blue accent.
- **Weekly Habits** — a list of all your weekly habits, shown with a purple accent.
- **Monthly Habits** — a list of all your monthly habits, shown with a cyan accent.

Each section shows a message like *"No daily habits yet."* when empty.

![habit section](/docs/images/habit_section.png)

### Right Panel — Your Progress

The right side of the dashboard shows your gamification stats:

- **Level badge** — your current level displayed in a circular badge.
- **Title** — your current rank title (e.g. *Beginner*, *Master*, *Legend*).
- **XP progress bar** — shows how far you are towards the next level.
- **Day Streak** — your current best streak across all habits.
- **Total Done** — the total number of habit completions you have made.
- **Today's Progress** — a progress bar showing how many of today's daily habits are done.
- **Achievements** — a grid of unlockable badges.

![right panel](/docs/images/right_panel.png)

---

## Managing Habits

### Creating a Recurring Habit

A recurring habit is something you want to do regularly — daily, weekly, or monthly.

1. Enter a **habit name** in the text field (e.g. "Go for a run").
2. Optionally, add a **description** for more context (e.g. "Run at least 2 km in the park").
3. Choose a **frequency** by clicking one of the three buttons:
   - **Daily** — you aim to complete this every day.
   - **Weekly** — you aim to complete this once per week.
   - **Monthly** — you aim to complete this once per month.
4. Click **Add Habit**.

![habit creation](/docs/images/habit_creation.png)

Your new habit appears in the corresponding section (Daily, Weekly, or Monthly).

> **Tip:** Adding a description helps the AI assign a more accurate difficulty and XP reward for your habit.

### Logging a One-Time Achievement

Sometimes you want to log something you did just once, without tracking it as a recurring habit.

1. Enter a **name** for the achievement (e.g. "Cleaned the garage").
2. Optionally, add a **description**.
3. Click **Track Now**.

You receive XP immediately and the accomplishment is recorded. No recurring habit is created.

### Editing a Habit

To change a habit's name, description, or frequency:

1. Find the habit in the list.
2. Click the **pencil icon** (✎) on the right side of the habit.
3. In the edit dialog that appears, make your changes.
4. Click **Save** to apply, or **Cancel** to discard changes.

![edit habit](/docs/images/edit_habit.png)

### Deleting a Habit

To permanently remove a habit:

1. Find the habit in the list.
2. Click the **× button** on the right side of the habit.

The habit is deleted immediately. This action cannot be undone.

---

## Completing Habits

### Marking a Habit as Complete

Each habit in the list has a **checkbox** on the left side.

1. Click the checkbox to mark the habit as **complete** for the current period (today for daily habits, this week for weekly habits, this month for monthly habits).
2. You will see:
   - A **green confirmation message** at the top (e.g. *"Morning run completed! +30 XP"*).
   - An **XP toast notification** in the bottom-right corner showing exactly how much XP you earned.
   - Your **XP bar**, **level**, and **streak** update in real time.

![Habit complete](/docs/images/xp_toast.png)

### Undoing a Completion

If you marked a habit as complete by mistake:

1. Click the checkbox again to **uncheck** it.
2. A message confirms the habit was unmarked.

---

## Experience Points (XP)

XP is the currency of your progress in HabitQuest. You earn XP every time you complete a habit, and XP drives your level progression.

### How XP is Calculated

Each habit has a **difficulty** rating from 1 to 5, shown as orange dots on the habit item. The base XP formula is:

```
XP = Difficulty × 10 × Frequency Multiplier
```

For example, a difficulty-3 daily habit earns **30 XP** per completion.

### Frequency Multipliers

Habits with less frequent schedules reward more XP per completion to reflect the larger commitment:

| Frequency | Multiplier | Example (Difficulty 3) |
|-----------|-----------|----------------------|
| Daily     | 1.0×      | 30 XP                |
| Weekly    | 1.5×      | 45 XP                |
| Monthly   | 2.0×      | 60 XP                |

### AI-Powered XP (Optional)

When enabled, HabitQuest uses AI to evaluate your habit description and assign a realistic difficulty rating. This means habits with more detailed descriptions get a more accurate XP reward. The AI considers factors like effort, time commitment, and complexity.

You can see the XP a habit will reward before creating it by looking at the **XP preview** during creation.

---

## Streaks

### How Streaks Work

A **streak** counts how many consecutive periods you have completed a habit without missing one.

- **Daily habits:** Your streak increases for each consecutive day you complete the habit. Miss a day, and the streak resets to zero.
- **Weekly habits:** Your streak increases for each consecutive week you complete the habit at least once.
- **Monthly habits:** Your streak increases for each consecutive month you complete the habit at least once.

Active streaks are shown as a **fire badge** (🔥) next to the habit, displaying the current streak number.

![streak](/docs/images/streak.png)

### Streak Bonus XP

Maintaining streaks rewards you with bonus XP on top of the base amount:

| Streak Length | Bonus      |
|---------------|------------|
| 3+ periods    | +10% XP    |
| 7+ periods    | +25% XP    |
| 14+ periods   | +50% XP    |
| 30+ periods   | +100% XP (double!) |

The XP toast notification will show the streak bonus separately, e.g. *"+30 XP (+15 streak bonus)"*.

> **Tip:** The longer your streak, the more XP you earn. Try not to break it!

---

## Levels and Titles

As you accumulate XP, you level up. Each level requires progressively more XP than the last.

Your current level is displayed in the **circular badge** on the right panel, and your **title** changes as you reach new milestones:

| Level Range | Title         |
|-------------|---------------|
| 1–2         | Beginner      |
| 3–4         | Apprentice    |
| 5–6         | Specialist    |
| 7–9         | Expert        |
| 10–14       | Master        |
| 15–19       | Grandmaster   |
| 20–29       | Legend         |
| 30+         | Mythic        |

The **XP progress bar** below your level shows how close you are to reaching the next level.

![level badge](/docs/images/level_badge.png)

---

## Achievements

HabitQuest features **6 achievement badges** that you can unlock by reaching certain milestones. Achievements are displayed in a grid on the right panel.

| Achievement      | Icon | How to Unlock                              |
|------------------|------|--------------------------------------------|
| **First Step**   | ⭐   | Complete your first habit                   |
| **Week Warrior** | 🛡️   | Build a 7-day streak                        |
| **Habit Master** | 👑   | Create 10 habits                            |
| **Consistent**   | 💎   | Achieve a 30-day streak                     |
| **Explorer**     | 🗺️   | Use all three frequencies (Daily, Weekly, Monthly) |
| **Legend**        | 🏆   | Reach 100 total completions                 |

![achievments](/docs/images/achievments.png)

**Locked achievements** appear greyed out. Once unlocked, they light up in full color with a glowing border. Hover over an achievement to see its name and requirement.

---

## Statistics and Today's Progress

The right panel displays three key statistics:

### Day Streak (🔥)
Your current best streak across all habits. This is the longest active streak you have right now.

### Total Done (✓)
The total number of habit completions you have ever made. This number only goes up.

### Today's Progress
A progress bar that shows how many of your **daily habits** you have completed today, displayed as *"X / Y"* where X is completed and Y is your total daily habits.

![progress](/docs/images/progress.png)

---

## Tips and Tricks

- **Start small.** Begin with just 2–3 daily habits. You can always add more once those become routine.
- **Use descriptions.** A detailed description helps the AI assign a more accurate difficulty, and it helps you remember exactly what you committed to.
- **Protect your streaks.** Streak bonuses can double your XP at 30+ days — that is a massive boost to your leveling speed.
- **Mix frequencies.** Having a mix of daily, weekly, and monthly habits keeps things interesting and unlocks the *Explorer* achievement.
- **Check in daily.** Even a quick look at your dashboard can keep you motivated and remind you of what you need to do.
- **Use one-time tracking for spontaneous wins.** Did something productive that is not a regular habit? Log it with *Track Now* and earn the XP.

---

*Happy questing!*
