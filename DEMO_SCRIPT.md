# CineMatch — Demo Script (2–3 minutes)

A ready-to-read walkthrough for presenting CineMatch to the class. Suggested member
to demo with: **Ana Souza** (works reliably and hits every part of the story below).
Have the app already running at `http://localhost:8501` before you start talking.

---

### 1. Business problem (0:00–0:20)

"Streaming growth today comes from *retention*, not new signups — the market is
saturated. Personalization is Netflix's strongest lever on that: showing each member
the right titles, in the right order, is what keeps them subscribed. CineMatch is a
small working model of how that personalization actually happens behind the home
screen — and how it's kept safe before anything reaches the member."

### 2. User input / starting point (0:20–0:40)

- Open the member dropdown: *"We start by picking a member — here's Ana Souza, a
  'Bingers' segment viewer in Brazil who likes Thriller and Drama, with an R
  maturity ceiling."*
- Point out the profile boxes (Segment / Territory / Favorite genres / Maturity
  ceiling): *"That's all the app knows about her — nothing else."*

### 3. What the application does (0:40–1:40)

- Point at the **Top picks** row: *"The app just scored every title in the catalog
  for Ana specifically — genre match, segment affinity, and popularity — and this
  row is the result, highest score first."*
- Point at one tagline: *"Each card also has a one-line tagline, written live by
  Google's Gemini AI, tailored to Ana's taste — not a generic blurb."*
- Scroll to **Needs review**: *"Now here's the important part. Before anything
  reaches the member, every title is checked — is it licensed in her country? Is it
  under her rating ceiling? Does it break an editorial policy? This title,
  'Red Room Diaries,' scored well enough to make the row, but it's tagged with a
  restricted genre — so it's held back for review instead of being shown. That's
  governance happening in real time, not as an afterthought."*

### 4. Output / recommendation (1:40–2:00)

"So what the member actually sees is a short, ranked, personalized, *pre-cleared*
list — six titles, each with a reason it's safe to show. Nothing reaches the screen
without passing that check first."

### 5. Business decision or action supported (2:00–2:30)

- Click **▶ Play** on one title: *"When Ana watches something, that's a signal. Watch
  the row — it just reordered, weighting her genres up for next time. This is the
  same 'data → decision → feedback' loop that drives the engagement numbers behind
  Netflix's real retention strategy — the more it's used, the sharper it gets."*
- "For the business, this is the point: personalization isn't just a nice-to-have
  feature, it's a live, measurable input into churn and engagement — the two metrics
  this whole strategy is trying to move."

### 6. What's simplified or mocked in this MVP (2:30–2:50)

"To build this in one classroom session, a few things are intentionally simplified:
the ranking is a transparent formula, not a trained model; the rights/availability
data is a small fictional table, not a live licensing system; and the thumbnails are
style cards by default — there's an optional button to generate an abstract AI
illustration instead, but it's not real movie-poster art. None of that changes the
core idea: rank, personalize, govern, and learn from feedback — the same loop a real
system runs, just at a scale we can show in three minutes."

---

## If asked "does this prove personalization reduces churn?"

Be direct: *"No — and that's an intentional limitation, not an oversight. This MVP
shows the mechanism, not the causal proof. Whether steering engagement actually
lowers churn is the open question the underlying strategy work leaves for further
testing."*

## Backup member (if Ana's flow ever looks off)

**Priya Nair** (Romantics, India) also demos well — her top-ranked title,
"Paper Moonlight," is flagged for a different reason (not licensed in her territory
rather than a policy issue), which is a good way to show that grounding checks
several *different* things, not just one rule.
