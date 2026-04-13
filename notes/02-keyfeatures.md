- Available attributes  
  - Metadata/identity: `id`, `title`, `artist`  
  - Descriptive tags: `genre`, `mood`  
  - Numeric audio/vibe features: `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`  

- Top 5 recommended features with brief rationale  
  1. `genre`  
     - High usefulness for broad similarity buckets; usually consistent and easy to interpret; strong first-pass impact on recommendation relevance.  
  2. `mood`  
     - Directly maps to user intent (“chill”, “intense”, “focused”); high practical impact for vibe matching, though tagging consistency can vary.  
  3. `energy`  
     - Strong predictor of perceived intensity/arousal; numeric and stable; very effective for sorting tracks from calm to high-drive.  
  4. `valence`  
     - Captures emotional positivity/negativity; complements energy well; improves quality by distinguishing, for example, “energetic-happy” vs “energetic-dark.”  
  5. `tempo_bpm`  
     - Objective and highly consistent; useful for pace matching (study, workout, driving), though alone it is weaker than energy+valence for full vibe.  

- Vibe alignment assessment (what fits, what does not, what to add)  
  - What fits  
    - `energy` + `valence` is a strong core for vibe because it mirrors a common emotion model: arousal (high/low) and affect (positive/negative).  
    - In real listening, this pair often separates major vibe zones well (calm/bright, calm/melancholic, intense/joyful, intense/aggressive).  
  - What does not fully fit  
    - Vibe perception is not only emotional intensity and positivity. Two songs with similar energy/valence can feel very different due to texture, rhythm feel, vocals, and production style.  
    - `mood` and `genre` help, but they are label-dependent and can be subjective or coarse.  
  - What to add (important missing dimensions)  
    - Keep using available `danceability` and `acousticness` in the model; both improve perceived vibe matching beyond energy/valence.  
    - If expanding features, add: loudness/dynamics, key/mode (major/minor), instrumentalness/vocal presence, timbral descriptors (brightness/warmth), lyrical sentiment/topic, and rhythmic feel (swing/syncopation).