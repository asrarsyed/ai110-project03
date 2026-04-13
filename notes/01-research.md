Major platforms like Spotify and YouTube use large-scale machine learning to predict “what you might want next” by combining two core ideas: collaborative filtering and content-based filtering. Collaborative filtering looks at behavior patterns across many users (for example, “people who liked A and B also liked C”). Content-based filtering looks at attributes of the item itself (for example, tempo, genre, mood, or video topic/style) and matches those to your past preferences. In practice, both platforms use many implicit signals (what you actually do) more heavily than explicit ratings, because behavior is abundant and often more reliable. Their production systems are hybrid, multi-stage pipelines: candidate generation (find likely items fast) plus ranking (order them based on predicted satisfaction).

| Aspect | Collaborative filtering | Content-based filtering |
|---|---|---|
| Data source | User-item interaction patterns across many users (plays, skips, watch time, likes, co-listens/co-watches) | Item features and descriptors (audio/video attributes, metadata, embeddings) + your own history |
| How it works in practice | Learns latent similarities: users with similar behavior get similar recommendations; items consumed together become related | Builds a profile of what you prefer (e.g., high-energy pop, long-form explainers) and finds items with similar features |
| Strengths | Excellent at discovering surprising items beyond obvious similarity; captures crowd wisdom and taste clusters | Works even with little community data; easy to explain (“similar to what you liked before”); good for niche/long-tail if features are rich |
| Weaknesses | Needs lots of interaction data; can reinforce popularity bias; can struggle with sparse users/items | Can over-specialize (“more of the same”); quality depends on feature engineering/model embeddings |
| Cold start | Weak for brand-new users/items with few interactions | Better for new items (if attributes known); limited for new users until some preference signal exists |
| Performs best when | Platform has large active user base and dense interaction logs | Item has high-quality descriptors (audio/video/text/image features) and user has clear feature-level preferences |

- **User behavior signals**
  - Likes/dislikes, thumbs up/down, “not interested”
  - Skips (early skip vs late skip), replays, repeat listens/views
  - Watch time, dwell time, completion rate, abandonment point
  - Search history, clicked results, query reformulations
  - Playlist additions, library saves, queue actions
  - Follows/subscriptions, channel or artist affinity
  - Shares, comments, social engagement
  - Session sequences: what was consumed before/after an item

- **Item/content attributes**
  - Audio features: tempo, key, loudness, energy, valence, danceability, acousticness, instrumentation
  - Categorical descriptors: genre, subgenre, language, creator/artist, release era
  - Mood/style tags: chill, upbeat, melancholic, focus, workout
  - Video features: topic, visual style, speech/music ratio, pacing, length
  - Text/metadata: title, description, tags, transcript/lyrics
  - Learned embeddings from deep models (audio embeddings, video embeddings, multimodal embeddings)

- **Context signals**
  - Time of day, day of week, seasonality
  - Device/surface (mobile, TV, smart speaker), app entry point
  - Session intent (active search vs passive autoplay)
  - Location/coarse region and language setting
  - Recent activity window (short-term mood) vs long-term taste profile
  - Network conditions/content availability constraints

Modern recommenders are hybrid because each method covers the other’s blind spots: collaborative filtering brings discovery from collective behavior, while content-based filtering handles new or sparse items and keeps recommendations relevant to known tastes. In systems like Spotify and YouTube, hybrid models plus strong ranking objectives (predicted satisfaction, retention, diversity, freshness) are what make recommendations feel both personal and dynamic.