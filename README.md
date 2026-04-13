# Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders (like Spotify or YouTube) use complex systems with user behavior, collaborative filtering, and content signals to rank results. This project keeps things simple by using a content-based approach that is easy to understand, adjust, and works well with small datasets without needing lots of user data.

- What features does each `Song` use in your system:
    - Each song is represented by identity fields plus a small set of categorical and numeric vibe features so the model can compare user intent directly to song attributes. This keeps matching behavior understandable while still capturing both style (`genre`, `mood`) and intensity/feel (`energy`, `valence`, `tempo_bpm`, etc.).
- What information does your `UserProfile` store:
    - The user profile stores preferred categorical tags (genre, mood) and target values for numeric audio features on a normalized 0-1 scale. In this simulation, the profile is explicit and static (entered preferences), rather than learned from long histories of implicit behavior.
- How does your `Recommender` compute a score for each song:
    - The recommender computes a categorical match score (`genre_score`, `mood_score`) plus a weighted numeric similarity score from feature distances (energy, valence, tempo, danceability, acousticness). It then combines them into one final score from 0 to 1 using tuned top-level weights (default: genre 0.35, mood 0.25, numeric 0.40), which makes user-to-song mapping explicit.
- How do you choose which songs to recommend:
  - After scoring all songs, the system filters by a minimum threshold (for example, >= 0.60), sorts descending, applies deterministic tie-breakers, and returns top-K. This ranking rule improves consistency and debuggability, while trading off some novelty/diversity that production systems often recover with extra reranking stages.

### Song Object (Core Attributes)

- `genre`: broad style bucket; high-impact first-pass relevance and easy interpretability.
- `mood`: intent-focused label (for example, chill/intense); helps align recommendations to session vibe.
- `energy`: strong signal of perceived intensity; separates calm vs high-drive tracks.
- `valence`: emotional positivity/negativity; complements energy for richer vibe matching.
- `tempo_bpm`: objective pace feature; useful for activity/session pace alignment.

### UserProfile Object (Core Attributes)

- `preferred_genre`: explicit stylistic preference used for exact categorical matching.
- `preferred_mood`: explicit session-intent target used for categorical matching.
- `target_energy`: desired intensity level for numeric distance scoring.
- `target_valence`: desired emotional tone used to reduce mood mismatch among similar songs.
- `target_tempo_bpm`: desired pacing target for rhythm and activity fit.

This design compares each user preference to matching song features, turns them into scores, and combines them into one final ranking. Unlike production systems, it has less personalization and no crowd-based learning, but it is easier to understand, control, and test.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
python -m pytest tests/ -v
```

You can add more tests in `tests/test_recommender.py`.