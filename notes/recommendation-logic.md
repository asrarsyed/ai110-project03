# Recommendation Scoring Logic (Final Recipe)

## 1) Scoring Logic (step-by-step)

Use a weighted point system with a maximum of **10.0 points** per song.

### A. Exact-match features (categorical)

1. **Genre match** (max **2.5** points)
	- If `song.genre` is in user preferred genres -> `+2.5`
	- Else -> `+0`

2. **Mood match** (max **2.0** points)
	- If `song.mood` is in user preferred moods -> `+2.0`
	- Else -> `+0`

Rationale:
- In this dataset, preferred genres (`lofi`, `ambient`, `jazz`) and preferred moods (`chill`, `focused`, `relaxed`) each cover about 25% of songs (5/20). Giving genre a slightly higher weight than mood keeps style identity strong while still respecting session intent.

### B. Similarity features (numeric, tolerance-based)

For each numeric feature, convert distance from user target into points with a simple piecewise rule.

Define:
- $d = |x - t|$ where $x$ is song value and $t$ is user target.
- Tolerance is from the user profile.

Similarity points function:

$$
sim(d, tol, maxPts) =
\begin{cases}
maxPts, & d \le tol \\
maxPts \cdot \left(1 - \frac{d - tol}{tol}\right), & tol < d < 2\,tol \\
0, & d \ge 2\,tol
\end{cases}
$$

This means:
- Full points inside tolerance.
- Linear drop-off outside tolerance.
- Zero after twice tolerance.

Apply to key numeric features:

3. **Energy similarity** (max **2.0** points)
	- `sim(abs(song.energy - 0.30), 0.12, 2.0)`

4. **Valence similarity** (max **1.5** points)
	- `sim(abs(song.valence - 0.60), 0.15, 1.5)`

5. **Tempo similarity** (max **1.5** points)
	- `sim(abs(song.tempo_bpm - 82), 10, 1.5)`

### C. Contrast penalty (to separate chill vs intense)

6. **High-contrast penalty**
	- If `abs(song.energy - 0.30) >= 0.30` -> `-1.0` point
	- If `abs(song.tempo_bpm - 82) >= 35` -> additional `-0.5` point

Rationale:
- This explicitly pushes down songs that are clearly far from the user's calm profile (for example, very high-energy, very high-tempo tracks), so "intense" styles do not rank near chill/focus tracks by accident.

### D. Final score formula

$$
score = genrePts + moodPts + energyPts + valencePts + tempoPts - contrastPenalty
$$

Clamp to range:

$$
finalScore = min(10, max(0, score))
$$

Sort songs by `finalScore` descending.

---

## 2) Why this weighting balance works

- **Genre (2.5) > Mood (2.0):** keeps stable taste identity while still allowing mood intent to matter.
- **Energy (2.0) is the strongest numeric feature:** most important for distinguishing calm/focused from intense.
- **Valence (1.5) + Tempo (1.5):** refine emotional tone and pace without overcomplicating the model.
- **Penalty layer:** guarantees meaningful separation between contrasting styles.

This recipe is intentionally simple, interpretable, and easy to tune by adjusting only a few point values.
