# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent to take my working `score_song` function (genre, mood, energy, valence, tempo rules) and extend it into the full `Recommender` class the tests expected: a `Song` dataclass, a `UserProfile` dataclass, `_convert_user_profile_to_dict`, and a `recommend`/`explain_recommendation` API on top of the existing dict-based scoring, without breaking the original `recommend_songs` function or its diversity re-ranking.

**Prompts used:**

- "Add a `Song` and `UserProfile` dataclass that match what `tests/test_recommender.py` expects, and wire up a `Recommender` class that reuses `score_song` internally instead of duplicating scoring logic."
- "Convert a `UserProfile` into the `user_prefs` dict shape `score_song` already accepts, including a reasonable default tolerance for energy."
- "Add alias tables for genre and mood (edm -> electronic, calm -> chill, etc.) so slightly different wording from a user still matches, and normalize/lowercase everything before comparing."
- "Add a profile reliability penalty that multiplies the score down when a profile is internally contradictory (e.g. chill mood but very high target energy)."

**What did the agent generate or change?**

- `src/recommender.py`: the `Song` and `UserProfile` dataclasses, `_convert_user_profile_to_dict`, `_canonical_genre`/`_canonical_mood` plus the `GENRE_ALIASES`/`MOOD_ALIASES` tables, `_normalize_user_prefs`, `_profile_reliability`, `_numeric_alignment` (used for tie-breaking), and the `Recommender.recommend` / `Recommender.explain_recommendation` methods.
- The diversity step in `recommend_songs` (penalizing repeated artists/genres while picking the next song) was drafted by the agent and then adjusted by hand.
- Ran `python -m pytest tests/ -v` after each change to check nothing in the existing dict-based API regressed.

**What did you verify or fix manually?**

- The agent's first version of `_profile_reliability` stacked penalties without a floor, which let a handful of contradictory answers push the multiplier to 0 and zero out the whole score; I added the `_clamp(reliability, 0.50, 1.0)` floor.
- I re-checked the energy/valence/tempo similarity math by hand against a couple of songs in `data/songs.csv` to make sure the `similarity()` linear falloff between `tolerance` and `2 * tolerance` matched what the reasons string reported.
- I tightened the diversity re-ranking penalty values (`-0.35` artist, `-0.20` genre) myself after the agent's initial values made the top-5 list swap out songs too aggressively on small catalogs.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

Strategy pattern, applied through the `score_config` dict (`DEFAULT_SCORE_CONFIG` / `_score_config`) rather than a full class hierarchy.

**How did AI help you brainstorm or implement it?**

I wanted to run the "stronger energy / weaker genre" and "mood scoring turned off" experiments mentioned in the README without copy-pasting `score_song`. I asked the agent for options, and it suggested either subclassing a `Scorer` base class per variant, or passing a small config object into the existing function and reading weights out of it at scoring time. I picked the config-object version since the project only needed a couple of tunable variants, not an open-ended family of scorers, so a lightweight strategy object was a better fit than a class hierarchy.

**How does the pattern appear in your final code?**

`DEFAULT_SCORE_CONFIG` and `_score_config()` in `src/recommender.py` define the swappable "strategy" (weights per feature plus an `enable_mood` toggle), and `score_song(user_prefs, song, score_config=None)` reads from whatever config is passed in instead of hardcoding weights. Running a variant is just calling `score_song(..., score_config={"weights": {"genre": 0.5, "energy": 2.0}})` or `{"enable_mood": False}`, which is how the weight-sensitivity experiments in the README/model card were produced.