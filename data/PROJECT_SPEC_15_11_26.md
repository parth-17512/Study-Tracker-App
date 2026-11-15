# StudyTrack -- Next Feature Improvements

## Purpose

Implement the following three improvements in StudyTrack. Before
changing code, inspect the existing project structure, data models,
timer/session logic, daily-goal settings, streak calculation, and UI
patterns. Reuse the current architecture and design system wherever
possible. Avoid breaking existing features or historical study records.

------------------------------------------------------------------------

## 1. Add a "Time Stamp" tab: 24-hour daily timeline

### Goal

Add a new navigation tab named **Time Stamp** that helps users
understand how they spend all 24 hours of a day---not only their study
time.

The view should make it easy to see: - Study sessions and their
durations. - The gaps between study sessions. - Time spent resting. -
Time spent inactive or not studying. - Time spent on other activities
entered by the user. - Time that has not yet been categorized.

### User flow

1.  The user opens the **Time Stamp** tab.
2.  The user selects a date (default: today).
3.  The user enters or edits time blocks for that day.
4.  Each block should have:
    -   Activity name or category.
    -   Start time.
    -   End time.
    -   Optional note.
5.  The app displays the day as a 24-hour timeline, from 00:00 to 24:00.
6.  Study blocks should be linked to existing study-session data
    wherever possible, rather than requiring users to enter the same
    study session twice.
7.  The user can add, edit, and delete manually entered non-study
    blocks.

### Visualization requirements

-   Show the complete 24-hour day in chronological order.
-   Use visually distinct categories for:
    -   Study
    -   Rest
    -   Other activity
    -   Inactive / unallocated time
-   Make the gaps between study sessions easy to identify.
-   Display each block's activity and duration.
-   Provide a daily summary showing total time for each category.
-   Show the total categorized time and remaining unallocated time.
-   Make the timeline usable on both desktop and mobile screens.
-   Include clear empty states and validation messages.

### Time calculation and validation

-   Calculate each block's duration from its start and end times.
-   Do not allow an end time earlier than or equal to its start time for
    a same-day block.
-   Prevent overlapping manually entered blocks.
-   Prevent manually entered blocks from overlapping existing study
    sessions.
-   The timeline must account for the full 24 hours. Any time not
    covered by a recorded activity should appear as **Unallocated /
    Inactive**; do not silently discard gaps.
-   Be clear that unallocated time is not necessarily confirmed
    inactivity---it is time the user has not categorized.
-   If overnight activities are supported, handle midnight crossings
    explicitly. Otherwise, keep blocks within one calendar day and
    explain this in validation.

### Suggested acceptance criteria

-   A user can select a date and view a full 24-hour timeline.
-   Existing study sessions appear automatically in the timeline.
-   A user can add, edit, and delete non-study activity blocks.
-   Gaps between study sessions are visible.
-   The daily category totals and unallocated time are calculated
    correctly.
-   The sum of all timeline segments is exactly 24 hours.
-   Overlapping or invalid blocks are rejected with a useful message.

------------------------------------------------------------------------

## 2. Prevent early completion of study sessions

### Goal

A user must not be able to mark a study session as completed before its
designated end time.

### Required behavior

-   Use the session's scheduled start time and designated duration/end
    time as the source of truth.
-   Do not allow the user to complete or end the session early through
    the UI.
-   Enforce this rule in the underlying session logic as well as the UI.
    Hiding or disabling a button alone is not sufficient.
-   If the user attempts to end a session early through another route or
    direct action, reject the action and show a clear message explaining
    when the session can be completed.
-   At the designated end time, allow the session to be completed
    normally.

### Study-time accounting

-   Add only the actual eligible completed duration to the user's total
    study time.
-   Never add the full scheduled duration when the user has not
    completed that duration.
-   Never count an incomplete or early-terminated session as a fully
    completed session.
-   Avoid double-counting when a completion action is retried.
-   Preserve the existing behavior for valid completed sessions unless
    it conflicts with these requirements.

### Important edge cases

-   Refreshing or reopening the app during an active session must not
    reset or incorrectly extend the session.
-   Use reliable timestamps rather than relying only on a browser
    countdown.
-   Handle app suspension, device sleep, and delayed completion actions
    correctly.
-   Ensure the backend or trusted data layer validates completion time
    if the project has one.
-   If the current architecture is client-only, centralize the
    validation in the session service/state logic so all completion
    paths use the same rule.

### Suggested acceptance criteria

-   A session cannot be completed before its scheduled end time.
-   An early completion attempt does not increase total study time.
-   A session completed at or after its scheduled end time is recorded
    correctly.
-   Repeated completion requests do not add study time more than once.
-   Refreshing the app does not bypass the restriction.

------------------------------------------------------------------------

## 3. Update the daily streak requirement

### Goal

A daily study streak should be maintained only when the user studies at
least **50% of their daily study goal**.

The current daily goal is **6 hours**, so the current minimum required
study time is:

**6 hours × 50% = 3 hours (180 minutes).**

### Required behavior

-   Calculate the streak threshold as 50% of the user's configured daily
    study goal.
-   With the current 6-hour goal, require at least 3 hours of eligible
    study time in a day.
-   If the user studies less than 3 hours, that day must not maintain or
    extend the streak.
-   If the user studies exactly 3 hours or more, that day qualifies.
-   Use completed, eligible study time only. Do not count incomplete
    sessions or scheduled time that was not actually completed.
-   Calculate the daily total across all eligible study sessions for
    that date.
-   Avoid counting the same session more than once.

### Configuration and historical data

-   Do not hardcode 3 hours if the daily goal can change. Derive the
    threshold from the configured goal.
-   If the daily goal changes, define and implement a consistent rule
    for which goal applies to each date. Prefer the goal value saved for
    that date, if the app already stores daily goal history.
-   If historical goal values are not stored, use the existing app
    convention and document the chosen behavior.
-   Recalculate streaks consistently from eligible daily totals without
    corrupting historical study data.

### Suggested acceptance criteria

-   Daily goal = 6 hours; study time = 2 hours 59 minutes → day does not
    qualify.
-   Daily goal = 6 hours; study time = exactly 3 hours → day qualifies.
-   Daily goal = 6 hours; study time = 3 hours 30 minutes → day
    qualifies.
-   Daily goal = 8 hours; study time = 3 hours 59 minutes → day does not
    qualify.
-   Daily goal = 8 hours; study time = exactly 4 hours → day qualifies.
-   Incomplete sessions do not contribute to the threshold.

------------------------------------------------------------------------

## Implementation instructions for the AI coding agent

1.  Inspect the existing codebase before implementing anything. Identify
    the framework, navigation structure, timer/session model,
    persistence layer, daily-goal configuration, and streak calculation.
2.  Follow existing naming, styling, state-management, and data-access
    conventions.
3.  Implement the three improvements as separate, focused changes.
4.  Keep existing user data and historical records safe. Add migrations
    only if required.
5.  Add or update unit tests for time calculations, session completion
    rules, and streak qualification.
6.  Add UI tests or integration tests where the current project supports
    them.
7.  Test boundary conditions, especially:
    -   Timeline blocks that touch but do not overlap.
    -   Invalid and overlapping time blocks.
    -   Early completion attempts.
    -   Completion exactly at the scheduled end time.
    -   Duplicate completion requests.
    -   Study time just below, exactly at, and above the streak
        threshold.
    -   Different daily goal values.
8.  Run the project's existing test suite, linting, and type checks. Fix
    regressions introduced by the changes.
9.  Do not replace existing libraries or restructure unrelated parts of
    the application without a clear technical need.
10. After implementation, provide a concise report containing:
    -   Files changed.
    -   Features implemented.
    -   Data-model or migration changes.
    -   Tests added and their results.
    -   Any assumptions, limitations, or unfinished work.

## Definition of done

All three improvements work with the existing StudyTrack application,
are responsive, preserve existing data, pass relevant tests, and follow
the acceptance criteria above.
