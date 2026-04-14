from math import sqrt
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

GENRE_ALIASES = {
    "edm": "electronic",
    "electro": "electronic",
    "indie-pop": "indie pop",
    "dnb": "drum and bass",
    "drum & bass": "drum and bass",
}

MOOD_ALIASES = {
    "calm": "chill",
    "energetic": "excited",
    "uplifted": "happy",
    "broody": "brooding",
}

DEFAULT_SCORE_CONFIG = {
    "weights": {
        "genre": 1.0,
        "mood": 1.0,
        "energy": 1.0,
        "valence": 1.0,
        "tempo": 1.0,
    },
    "enable_mood": True,
}


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _convert_user_profile_to_dict(user: UserProfile) -> Dict:
    """Convert a UserProfile into the dict format expected by score_song()."""
    energy_tolerance = max(0.10, user.target_energy * 0.15)

    return {
        "genre": [user.favorite_genre],
        "mood": [user.favorite_mood],
        "energy": {"target": user.target_energy, "tolerance": energy_tolerance},
        "likes_acoustic": user.likes_acoustic,
    }


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _coerce_pref_list(value: object) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip().lower() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip().lower()]
    return []


def _canonical_genre(value: str) -> str:
    cleaned = value.strip().lower()
    return GENRE_ALIASES.get(cleaned, cleaned)


def _canonical_mood(value: str) -> str:
    cleaned = value.strip().lower()
    return MOOD_ALIASES.get(cleaned, cleaned)


def _score_config(score_config: Optional[Dict]) -> Dict:
    merged = {
        "weights": dict(DEFAULT_SCORE_CONFIG["weights"]),
        "enable_mood": DEFAULT_SCORE_CONFIG["enable_mood"],
    }
    if not isinstance(score_config, dict):
        return merged

    weights = score_config.get("weights", {})
    if isinstance(weights, dict):
        for key in merged["weights"]:
            value = weights.get(key)
            if isinstance(value, (int, float)):
                merged["weights"][key] = max(0.0, float(value))

    if isinstance(score_config.get("enable_mood"), bool):
        merged["enable_mood"] = score_config["enable_mood"]
    return merged


def _normalize_numeric_pref(
    value: object,
    *,
    default_target: float,
    default_tolerance: float,
    min_target: float,
    max_target: float,
    max_tolerance: float,
) -> Dict[str, float]:
    target = default_target
    tolerance = default_tolerance
    if isinstance(value, dict):
        try:
            target = float(value.get("target", default_target))
        except (TypeError, ValueError):
            target = default_target
        try:
            tolerance = float(value.get("tolerance", default_tolerance))
        except (TypeError, ValueError):
            tolerance = default_tolerance

    return {
        "target": _clamp(target, min_target, max_target),
        "tolerance": _clamp(tolerance, 0.0, max_tolerance),
    }


def _normalize_user_prefs(user_prefs: Dict) -> Dict:
    genre_prefs = [_canonical_genre(value) for value in _coerce_pref_list(user_prefs.get("genre", []))]
    mood_prefs = [_canonical_mood(value) for value in _coerce_pref_list(user_prefs.get("mood", []))]

    return {
        "genre": genre_prefs,
        "mood": mood_prefs,
        "energy": _normalize_numeric_pref(
            user_prefs.get("energy", {}),
            default_target=0.30,
            default_tolerance=0.12,
            min_target=0.0,
            max_target=1.0,
            max_tolerance=0.25,
        ),
        "valence": _normalize_numeric_pref(
            user_prefs.get("valence", {}),
            default_target=0.60,
            default_tolerance=0.15,
            min_target=0.0,
            max_target=1.0,
            max_tolerance=0.25,
        ),
        "tempo_bpm": _normalize_numeric_pref(
            user_prefs.get("tempo_bpm", {}),
            default_target=82,
            default_tolerance=10,
            min_target=40.0,
            max_target=220.0,
            max_tolerance=25.0,
        ),
    }


def _profile_reliability(user_prefs: Dict) -> float:
    normalized = _normalize_user_prefs(user_prefs)
    reliability = 1.0

    mood_set = set(normalized["mood"])
    energy_target = normalized["energy"]["target"]
    valence_target = normalized["valence"]["target"]
    tempo_target = normalized["tempo_bpm"]["target"]

    if not normalized["genre"] and not normalized["mood"]:
        reliability -= 0.20

    if any(mood in mood_set for mood in {"chill", "calm", "relaxed", "sad"}) and energy_target >= 0.85:
        reliability -= 0.15
    if any(mood in mood_set for mood in {"sad", "moody", "brooding", "anxious", "wistful"}) and valence_target >= 0.75:
        reliability -= 0.10
    if any(mood in mood_set for mood in {"happy", "excited", "playful", "triumphant"}) and valence_target <= 0.35:
        reliability -= 0.10
    if energy_target >= 0.85 and tempo_target <= 85:
        reliability -= 0.10
    if energy_target <= 0.25 and tempo_target >= 150:
        reliability -= 0.10

    raw_numeric = {
        "energy": user_prefs.get("energy", {}),
        "valence": user_prefs.get("valence", {}),
        "tempo_bpm": user_prefs.get("tempo_bpm", {}),
    }
    for key, limits in {
        "energy": (0.0, 1.0, 0.25),
        "valence": (0.0, 1.0, 0.25),
        "tempo_bpm": (40.0, 220.0, 25.0),
    }.items():
        raw_value = raw_numeric.get(key, {})
        if not isinstance(raw_value, dict):
            continue
        try:
            raw_target = float(raw_value.get("target"))
        except (TypeError, ValueError):
            raw_target = None
        try:
            raw_tolerance = float(raw_value.get("tolerance"))
        except (TypeError, ValueError):
            raw_tolerance = None

        min_target, max_target, max_tolerance = limits
        if raw_target is not None and not (min_target <= raw_target <= max_target):
            reliability -= 0.05
        if raw_tolerance is not None and not (0.0 <= raw_tolerance <= max_tolerance):
            reliability -= 0.05

    return _clamp(reliability, 0.50, 1.0)


def _numeric_alignment(user_prefs: Dict, song: Dict) -> float:
    normalized = _normalize_user_prefs(user_prefs)
    energy_distance = abs(float(song.get("energy", 0.0)) - normalized["energy"]["target"])
    valence_distance = abs(float(song.get("valence", 0.0)) - normalized["valence"]["target"])
    tempo_distance = abs(float(song.get("tempo_bpm", 0.0)) - normalized["tempo_bpm"]["target"])

    energy_alignment = 1.0 - min(energy_distance / 1.0, 1.0)
    valence_alignment = 1.0 - min(valence_distance / 1.0, 1.0)
    tempo_alignment = 1.0 - min(tempo_distance / 180.0, 1.0)

    return (energy_alignment + valence_alignment + tempo_alignment) / 3.0


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        """Initialize the recommender with a catalog of songs."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs for a user ranked by score."""
        user_prefs = _convert_user_profile_to_dict(user)
        scored_songs = []

        for song in self.songs:
            song_dict = {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "genre": song.genre,
                "mood": song.mood,
                "energy": song.energy,
                "tempo_bpm": song.tempo_bpm,
                "valence": song.valence,
                "danceability": song.danceability,
                "acousticness": song.acousticness,
            }
            score, _ = score_song(user_prefs, song_dict)
            scored_songs.append((song, score))

        # Sort by score descending
        ranked = sorted(scored_songs, key=lambda x: x[1], reverse=True)

        # Return top k Song objects
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a readable explanation for a song's recommendation score."""
        user_prefs = _convert_user_profile_to_dict(user)
        song_dict = {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
        }
        _, reasons = score_song(user_prefs, song_dict)

        # Join reasons into readable sentence
        return ". ".join(reasons) if reasons else "No matching criteria"


def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into a list of dictionaries."""
    import csv

    songs = []
    numeric_fields = {"id", "energy", "tempo_bpm", "valence", "danceability", "acousticness"}

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = {}
            for key, value in row.items():
                if key in numeric_fields:
                    song[key] = float(value) if "." in value else int(value)
                else:
                    song[key] = value
            songs.append(song)

    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(
    user_prefs: Dict, song: Dict, score_config: Optional[Dict] = None
) -> Tuple[float, List[str]]:
    """Score a single song against user preferences and return reasons."""
    normalized = _normalize_user_prefs(user_prefs)
    config = _score_config(score_config)
    score = 0.0
    reasons = []

    def similarity(distance: float, tolerance: float, max_points: float) -> float:
        """Compute similarity points based on distance from target."""
        if distance <= tolerance:
            return max_points
        elif distance < 2 * tolerance:
            return max_points * (1 - (distance - tolerance) / tolerance)
        else:
            return 0.0

    # Rule 1: Genre match (max 2.5 points)
    preferred_genres = normalized["genre"]
    preferred_moods = normalized["mood"]
    song_genre = _canonical_genre(str(song.get("genre", "")))
    song_mood = _canonical_mood(str(song.get("mood", "")))

    genre_weight = (
        (2.5 * config["weights"]["genre"]) / sqrt(len(preferred_genres))
        if preferred_genres
        else 0.0
    )
    if preferred_genres and song_genre in preferred_genres:
        score += genre_weight
        reasons.append(f"genre match (+{genre_weight:.2f})")

    # Rule 2: Mood match (max 2.0 points)
    mood_weight = (
        (2.0 * config["weights"]["mood"]) / sqrt(len(preferred_moods))
        if preferred_moods
        else 0.0
    )
    if config["enable_mood"] and preferred_moods and song_mood in preferred_moods:
        score += mood_weight
        reasons.append(f"mood match (+{mood_weight:.2f})")

    # Extract energy target and tolerance
    energy_target = normalized["energy"]["target"]
    energy_tolerance = normalized["energy"]["tolerance"]

    # Rule 3: Energy similarity (max 2.0 points)
    if "energy" in song:
        energy_distance = abs(float(song["energy"]) - energy_target)
        energy_points = similarity(
            energy_distance, energy_tolerance, 2.0 * config["weights"]["energy"]
        )
        if energy_points > 0:
            score += energy_points
            reasons.append(f"energy similarity (+{energy_points:.2f})")

    # Extract valence target and tolerance
    valence_target = normalized["valence"]["target"]
    valence_tolerance = normalized["valence"]["tolerance"]

    # Rule 4: Valence similarity (max 1.5 points)
    if "valence" in song:
        valence_distance = abs(float(song["valence"]) - valence_target)
        valence_points = similarity(
            valence_distance, valence_tolerance, 1.5 * config["weights"]["valence"]
        )
        if valence_points > 0:
            score += valence_points
            reasons.append(f"valence similarity (+{valence_points:.2f})")

    # Extract tempo target and tolerance
    tempo_target = normalized["tempo_bpm"]["target"]
    tempo_tolerance = normalized["tempo_bpm"]["tolerance"]

    # Rule 5: Tempo similarity (max 1.5 points)
    if "tempo_bpm" in song:
        tempo_distance = abs(float(song["tempo_bpm"]) - tempo_target)
        tempo_points = similarity(
            tempo_distance, tempo_tolerance, 1.5 * config["weights"]["tempo"]
        )
        if tempo_points > 0:
            score += tempo_points
            reasons.append(f"tempo similarity (+{tempo_points:.2f})")

    # Rule 6: Contrast penalty
    penalty = 0.0
    if "energy" in song:
        energy_distance = abs(float(song["energy"]) - energy_target)
        # Skip penalty for high-energy targets (use only for chill profiles)
        if energy_target < 0.5 and energy_distance >= 0.30:
            penalty += 1.0

    if "tempo_bpm" in song:
        tempo_distance = abs(float(song["tempo_bpm"]) - tempo_target)
        if tempo_distance >= 35:
            penalty += 0.5

    if penalty > 0:
        score -= penalty
        reasons.append(f"contrast penalty (-{penalty:.1f})")

    reliability = _profile_reliability(user_prefs)
    if reliability < 1.0:
        score *= reliability
        reasons.append(f"profile reliability x{reliability:.2f}")

    if not preferred_genres and not preferred_moods and score > 6.0:
        score = 6.0
        reasons.append("no-category cap (max 6.0)")

    # Clamp to [0, 10]
    final_score = min(10.0, max(0.0, score))

    return (final_score, reasons)


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    score_config: Optional[Dict] = None,
    diversify: bool = True,
) -> List[Tuple[Dict, float, str]]:
    """Return top-k scored songs with a human-readable explanation string."""
    scored_songs = []

    for song in songs:
        score, reasons = score_song(user_prefs, song, score_config=score_config)
        explanation = ". ".join(reasons) if reasons else "No matching criteria"
        tie_break = _numeric_alignment(user_prefs, song)
        scored_songs.append((song, score, explanation, tie_break))

    # Sort by score descending and break ties by numeric closeness to targets.
    ranked = sorted(scored_songs, key=lambda x: (x[1], x[3]), reverse=True)
    if not diversify:
        return [(song, score, explanation) for song, score, explanation, _ in ranked[:k]]

    selected = []
    used_artists = set()
    used_genres = set()
    remaining = list(ranked)

    while remaining and len(selected) < k:
        best_idx = 0
        best_adjusted = float("-inf")
        best_tie_break = float("-inf")
        for idx, (song, score, explanation, tie_break) in enumerate(remaining):
            adjusted = score
            artist = str(song.get("artist", "")).strip().lower()
            genre = _canonical_genre(str(song.get("genre", "")))
            if artist in used_artists:
                adjusted -= 0.35
            if genre in used_genres:
                adjusted -= 0.20
            if adjusted > best_adjusted or (adjusted == best_adjusted and tie_break > best_tie_break):
                best_idx = idx
                best_adjusted = adjusted
                best_tie_break = tie_break

        picked = remaining.pop(best_idx)
        selected.append(picked)
        used_artists.add(str(picked[0].get("artist", "")).strip().lower())
        used_genres.add(_canonical_genre(str(picked[0].get("genre", ""))))

    return [(song, score, explanation) for song, score, explanation, _ in selected]
