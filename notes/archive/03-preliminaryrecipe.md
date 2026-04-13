**Algorithm Recipe Plan (Readable Version)**

### 1. Goal
Build a two-stage recommender:

1. **Scoring Rule (single song):** compute one match score from 0 to 1 for each song.
2. **Ranking Rule (song list):** sort/filter scored songs into final recommendations.

This separation keeps the system easy to tune and debug.

---

### 2. Scoring Rule Blueprint

#### 2.1 Categorical scores
- Genre match:
  - `genre_score = 1` if song genre = preferred genre, else `0`
- Mood match:
  - `mood_score = 1` if song mood = preferred mood, else `0`

#### 2.2 Numeric feature distance
For each numeric feature \(j\) (energy, valence, tempo, danceability, acousticness):
- Normalize to 0-1 first.
- Distance:  
  \[
  d_j = |x_j - p_j|
  \]
  where \(x_j\) is song value, \(p_j\) is user preference.

#### 2.3 Two valid distance-to-score options
1. **Linear penalty**
\[
s_j = 1 - d_j
\]
2. **Squared penalty**
\[
s_j = (1 - d_j)^2
\]

Quick comparison:
- Linear is more forgiving.
- Squared is stricter; punishes mismatch faster.

#### 2.4 Aggregate numeric score
\[
num\_score = \frac{\sum_j \alpha_j s_j}{\sum_j \alpha_j}
\]
where \(\alpha_j\) are internal numeric feature weights.

#### 2.5 Final song score
\[
S = w_g \cdot genre\_score + w_m \cdot mood\_score + w_n \cdot num\_score
\]
with:
\[
w_g + w_m + w_n = 1
\]

---

### 3. Weight Recommendations (Initial)

Use this starting point:

- \(w_g = 0.35\) (genre)
- \(w_m = 0.25\) (mood)
- \(w_n = 0.40\) (numeric)

Numeric internal weights:
- energy 0.30
- valence 0.25
- tempo 0.20
- danceability 0.15
- acousticness 0.10

Tradeoff guidance:
1. **Genre > Mood** when you want stylistic consistency and fewer cross-style jumps.
2. **Mood > Genre** for session intent playlists (focus, sleep, workout, chill-now), or when mood labels are high quality.
3. Keep numeric weight high because energy + valence + tempo usually drive perceived vibe quality.

Mood-first alternative:
- \(w_g = 0.20,\; w_m = 0.40,\; w_n = 0.40\)

---

### 4. Worked Example (3 Songs, Step-by-Step)

User preference:
- genre = Pop
- mood = Chill
- energy = 0.40
- valence = 0.70
- tempo = 100 BPM  
Use linear numeric scoring and top-level weights \(0.35, 0.25, 0.40\).

| Song | Genre | Mood | num_score | genre_score | mood_score | Final \(S\) |
|---|---|---:|---:|---:|---:|---:|
| A | Pop | Chill | 0.9521 | 1 | 1 | 0.9808 |
| B | Pop | Intense | 0.7292 | 1 | 0 | 0.6417 |
| C | Indie | Chill | 0.9458 | 0 | 1 | 0.6283 |

Ranking result: **A > B > C**

Key takeaway:
- B beats C despite lower numeric vibe because B gets genre match and C does not.
- This is exactly what weight tuning controls.

---

### 5. Ranking Rule Blueprint (List-Level)

After every song gets score \(S\):

1. **Minimum-score threshold**
   - Keep only songs with \(S \ge \tau\), start with \(\tau = 0.60\).
2. **Sort descending**
   - Higher \(S\) first.
3. **Tie-breaking**
   - Use this order:
   1. Higher mood score
   2. Smaller tempo distance
   3. Stable key (song id ascending)
4. **Top-K selection**
   - Return first \(K\) songs (e.g., 10 or 20).
5. **Optional diversity pass**
   - Prevent near-duplicates (same artist/very similar feature vectors).
   - Use lightweight rerank (for example, MMR) if list feels repetitive.

---

### 6. Plan to Deploy This in Your Project

1. **Choose one numeric penalty first**  
   Start with linear for stable behavior.
2. **Lock baseline weights**  
   Use recommended defaults above.
3. **Run offline evaluation on your CSV**  
   Check whether top results feel right for different preference profiles.
4. **Tune weights by scenario**  
   Keep two profiles: default vs mood-first.
5. **Add diversity only after baseline is good**  
   Avoid introducing too many knobs early.
6. **Document chosen defaults**  
   Keep a short “why these weights” note for future tuning.