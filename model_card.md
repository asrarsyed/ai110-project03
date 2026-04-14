# Model Card: LoopIntensity

## Model Name
**LoopIntensity**

## Goal / Task
This recommender suggests top songs for a user profile.  
It tries to match the user on genre, mood, and vibe features like energy, valence, and tempo.  
The goal is to return songs that feel close to the user’s current taste.

## Data Used
The dataset has 20 songs from `data/songs.csv`.  
Each song has genre, mood, energy, tempo, valence, danceability, and acousticness.  
The catalog is small, so coverage is limited.  
Some genres and moods have only one or two songs, which limits variety.

## Algorithm Summary
Each song gets points from simple rules.  
It gets points for genre match, mood match, and closeness to target energy, valence, and tempo.  
It loses points when the song strongly conflicts with the profile.  
Scores are clamped to 0–10, then songs are ranked by score.  
The system also normalizes aliases, penalizes contradictory profiles, and reranks to improve diversity in top results.

## Observed Behavior / Biases
Results are deterministic, so the same input gives the same ranking every run.  
Profiles with rare labels can get weaker results than common profiles.  
In fairness checks, the rare-label group had lower average top-5 scores than chill and high-energy groups.  
The model can still miss nuance because it depends on a small label-based catalog.

## Evaluation Process
I tested standard presets like High-Energy Pop, Chill Lofi, Deep Intense Rock, Upbeat Dance, and Soft Acoustic Calm.  
I also tested adversarial profiles, including conflicting preferences, no-category profiles, and category-spam profiles.  
I ran sensitivity experiments with weight shifts and mood-off scoring.  
One key result was stable top-5 overlap in one test even when scores changed, which showed rank stability but confidence movement.

## Intended Use and Non-Intended Use
Intended use: classroom demos and simple music preference experiments.  
It is good for showing transparent scoring behavior and testing profile design.  
Non-intended use: production music streaming recommendations for real users at scale.  
It should not be used for high-stakes personalization decisions.

## Ideas for Improvement
1. Expand the dataset with more songs and better label coverage.
2. Learn feature weights from feedback instead of fixed manual weights.
3. Add richer explainability and stronger fairness checks across more profile groups.
