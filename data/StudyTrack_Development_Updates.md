# StudyTrack --- Development Update Specification

## Goal

Implement the following improvements in StudyTrack while preserving
existing user data, current features, and the app's modular
architecture. Before changing code, inspect the existing codebase and
identify the relevant UI components, services, database models, and
tests. Reuse existing patterns where possible; do not introduce
duplicate systems.

## 1. Replace Recent Activity with a Full-Width GitHub-Style Study Graph

### Requested change

-   Remove the **Recent Activity** tab/section from the main screen.
-   Use the freed-up space on the left side of the screen for a larger
    GitHub-style study contribution graph.
-   The graph should make study consistency easy to understand at a
    glance.

### Requirements

-   Display daily study activity using a contribution-style heatmap.
-   Use actual persisted study-session data; do not use mock or
    hard-coded values.
-   Keep the graph responsive and make good use of the available
    left-side screen area.
-   Use clear intensity levels to represent study time or activity.
-   Include useful date and study-duration details on hover or
    selection, if supported by the current UI framework.
-   Handle days with no study activity clearly.
-   Keep the layout usable at different window sizes and avoid clipping
    or excessive empty space.

### Acceptance criteria

-   Recent Activity is no longer visible on the main screen.
-   The contribution graph occupies the intended freed-up space.
-   Graph values match the study-session records in the database.
-   The graph updates when new sessions are recorded.
-   Existing study history is not deleted or modified.

## 2. AI-Powered Subject Distribution Insights

### Requested change

Inside **Analytics → Subject Distribution**, add an AI-powered feature
that groups similar study subjects/topics into broader learning areas
and summarizes the combined study time.

### Example

If the user has studied: - Python --- 4 hours - Python Programming --- 3
hours - Python Projects --- 2 hours

The feature may group these under **Python** and report **9 hours**,
while retaining access to the original entries.

### Requirements

-   Identify semantically similar subject/session names and group them
    under a clear common label.
-   Show the total study time for each group.
-   Make the grouping explainable: show which original subjects were
    included in each group.
-   Do not silently merge, rename, or overwrite the user's original
    subject/session records.
-   Prefer deterministic aggregation for totals. Use an LLM only for
    semantic grouping and concise labels/summaries.
-   Handle ambiguous names conservatively. Avoid grouping unrelated
    topics just because they share a word.
-   Provide a way to inspect the original subjects behind each group.
-   If AI is unavailable, keep the existing subject distribution
    working.

### Acceptance criteria

-   Similar subjects can be presented as broader learning areas.
-   Group totals equal the sum of their original study durations.
-   Original records remain unchanged.
-   The feature handles empty data and AI-provider failures gracefully.

## 3. Support Gemini and Free-Tier Hosted LLM APIs

### Requested change

The app uses Google Gemini and should also allow the user to configure a
hosted LLM API with a free tier, using that provider's API key. Free-tier
availability and quotas vary by provider.

### Requirements

-   Keep provider-specific communication behind the shared provider
    abstraction so AI Coach and subject grouping can use the configured
    providers without duplicating application logic.
-   Support Google Gemini and user-configured OpenAI-compatible hosted
    APIs, including the provider's base URL, model ID, and API key.
-   Support configurable provider priority/fallback between configured
    hosted providers.
-   Handle rate limits, quota exhaustion, timeouts, connection failures,
    and malformed responses.
-   Do not automatically send private study notes or personal data to a
    cloud provider without clear user configuration/consent.
-   Keep API keys out of source code and logs. Store credentials using
    the app's existing secure configuration approach.
-   Show which provider/model handled a request and give a useful error
    when all configured providers fail.
-   Never claim that the app has unlimited tokens. Hosted provider
    quotas, rate limits, and terms vary.

### Acceptance criteria

-   The app reports provider availability and useful setup errors.
-   Gemini quota failures can trigger the configured fallback behavior.
-   Provider failures do not crash the app or leave the UI stuck.
-   Existing Gemini functionality continues to work.
-   The user can configure a compatible hosted API using its API key.
-   No secrets or private notes are exposed in logs or sent to
    unconfigured providers.

## 4. Allow Editing Original Session Names from the Timer Page

### Requested change

Add an editing control on the **Timer** page so the user can edit the
original name of a study session and organize learning into well-defined
categories.

### Requirements

-   Allow the user to edit a session name from the timer page.
-   Save the updated name to persistent storage.
-   Ensure the change is reflected consistently wherever that session
    name appears, including analytics and history.
-   Preserve the session's date, duration, and other metadata when
    editing its name.
-   Validate names (for example, reject blank names and trim accidental
    surrounding whitespace).
-   If the current data model separates sessions from
    subjects/categories, follow the existing relationship design rather
    than changing historical records unexpectedly.
-   Provide clear save/cancel feedback and handle database errors
    safely.

### Acceptance criteria

-   A session name can be edited successfully.
-   The updated name persists after restarting the app.
-   Related views show the updated name.
-   Editing a name does not change the recorded study duration or
    timestamps.

## 5. Fix and Improve the AI Coach's Retrieval and Analytics

### Current problems

The AI Coach often gives empty or irrelevant answers. It appears unable
to retrieve past notes and study-session history reliably.

Examples of failed questions: - "I want a week-by-week analysis for the
last 4 weeks of my studies." --- The response is empty. - "What notes
did I write today?" --- The response says it could not find highly
relevant notes. - Questions about older notes and past study hours are
not answered reliably.

### Requested change

Audit and improve the complete AI Coach data-retrieval and response
pipeline so it can answer questions about both personal notes and
historical study activity.

### Requirements

#### A. Inspect the existing pipeline

-   Trace the full flow from user question to retrieval, context
    construction, LLM call, and displayed response.
-   Inspect note indexing/embedding, metadata, database queries, date
    filtering, retrieval ranking, prompt construction, token limits, and
    error handling.
-   Identify the actual root causes before replacing components.
-   Add useful diagnostic logging without logging note contents, API
    keys, or other private data.

#### B. Retrieve notes reliably

-   Support questions about notes written today, yesterday, within a
    date range, and in the past.
-   Use note metadata and database filters for exact date-based
    questions instead of relying only on semantic similarity search.
-   Retrieve note title, content, creation/update date, and relevant
    folder/category metadata where available.
-   Ensure newly created or edited notes become searchable promptly.
-   Handle timezone boundaries consistently with the app's configured
    local timezone.
-   If no notes match, say so clearly rather than returning an unrelated
    answer.

#### C. Retrieve study history reliably

-   Use structured database queries for study-session questions such as:
    -   Total study time today or this week.
    -   Study time by subject.
    -   Week-by-week study time for the last four weeks.
    -   Most and least studied subjects.
    -   Changes in study time across date ranges.
-   Calculate totals and comparisons in application code or SQL, not by
    asking the LLM to do arithmetic from raw records.
-   Define week boundaries consistently and label the date range used in
    each weekly result.
-   Distinguish zero study time from missing/unavailable data.

#### D. Combine retrieval with the LLM

-   Route questions to the right data source:
    -   Notes questions → note database/search.
    -   Study-time questions → structured analytics queries.
    -   Questions involving both → retrieve both sources.
-   Pass only relevant, bounded context to the LLM.
-   Ask the LLM to summarize retrieved facts without inventing missing
    information.
-   Include dates, totals, and source details where useful.
-   If retrieval returns no data, explain what was searched and ask a
    focused follow-up only when needed.
-   If the provider fails or returns an empty response, show a clear
    error/fallback message instead of a blank answer.

#### E. Testing and quality

Add tests for at least these scenarios: 1. Retrieve notes created today.
2. Retrieve notes from a specified past date. 3. Retrieve notes across a
date range. 4. Return a useful response when no notes exist for the
requested period. 5. Calculate study time for each of the last four
weeks. 6. Handle weeks with zero study time. 7. Group study time by
subject. 8. Answer a question that requires both notes and study
history. 9. Handle unavailable LLM providers and empty/malformed LLM
responses. 10. Verify that dates are interpreted using the configured
timezone.

### Acceptance criteria

-   The four-week study analysis returns four clearly labeled weekly
    results when sufficient history exists.
-   "What notes did I write today?" retrieves notes using their dates,
    not only semantic similarity.
-   The Coach can answer questions about past study hours and subjects
    from real database records.
-   Answers are grounded in retrieved data and do not invent totals or
    notes.
-   Empty results and provider errors produce clear messages, never a
    blank response.
-   Existing Coach functionality remains available.

## 6. Engineering Rules

-   Inspect the current architecture before implementation.
-   Preserve existing user data and backward compatibility.
-   Do not delete or rewrite historical study records.
-   Keep UI, business logic, database access, and LLM-provider code
    separated.
-   Use database migrations for schema changes; never reset the database
    to apply an update.
-   Add or update automated tests for every changed feature.
-   Handle loading, empty, success, and error states in the UI.
-   Avoid hard-coded paths, API keys, model names, and provider
    assumptions.
-   Do not make unrelated UI or architecture changes.
-   Follow the project's existing code style and conventions.

## 7. Suggested Implementation Order

1.  Inspect the codebase and write a short impact analysis for all five
    changes.
2.  Fix AI Coach retrieval and add tests for notes and study analytics.
3.  Introduce the LLM provider abstraction and add hosted API fallback
    support.
4.  Add session-name editing.
5.  Add AI-powered subject grouping.
6.  Replace Recent Activity with the expanded contribution graph.
7.  Run the full test suite and verify database/data preservation.

## 8. Final Delivery Requirements for the Development Agent

When implementation is complete, provide: - A summary of
files/components changed. - The root causes found in the AI Coach and
how they were fixed. - New configuration/setup steps for hosted
providers. - Database migration details, if any. - Tests added and their
results. - Known limitations, especially provider quotas and local
hardware requirements. - Any feature that could not be completed, with
the reason.

Do not mark a feature complete unless its acceptance criteria have been
tested.
