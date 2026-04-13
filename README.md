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
    - Each song includes identity fields plus the core matching features `genre`, `mood`, `energy`, `valence`, and `tempo_bpm`, so the system can compare style, vibe, and pace in a clear way.
- What information does your `UserProfile` store:
    - The profile stores lists of preferred `genre` and `mood`, plus target and tolerance values for `energy`, `valence`, and `tempo_bpm`; these values are entered directly instead of learned from behavior history.
- How does your `Recommender` compute a score for each song:
    - The recommender uses a 10-point rule: genre match adds `+2.5`, mood match adds `+2.0`, energy/valence/tempo add similarity points based on distance from targets, and a contrast penalty lowers scores for strong chill-vs-intense mismatch before clamping to `0-10`.
- How do you choose which songs to recommend:
  - After every song is scored, the system stores the result, sorts all songs by final score from highest to lowest, and returns the top-K recommendations.

### Song Object (Core Attributes)

- `genre`: broad style bucket; high-impact first-pass relevance and easy interpretability.
- `mood`: intent-focused label (for example, chill/intense); helps align recommendations to session vibe.
- `energy`: strong signal of perceived intensity; separates calm vs high-drive tracks.
- `valence`: emotional positivity/negativity; complements energy for richer vibe matching.
- `tempo_bpm`: objective pace feature; useful for activity/session pace alignment.

### UserProfile Object (Core Attributes)

- `genre`: list of preferred genres used for exact categorical matching.
- `mood`: list of preferred moods used for exact categorical matching.
- `energy` (`target`, `tolerance`): desired intensity level and acceptable range.
- `valence` (`target`, `tolerance`): desired emotional tone and acceptable range.
- `tempo_bpm` (`target`, `tolerance`): desired pace and acceptable range.

This design follows a simple flow: take user preferences, load songs, score each song with the same rules, then rank results. It has less personalization than production systems, but it is easy to understand, tune, and test.

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