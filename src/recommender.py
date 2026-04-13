from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/taest_recommender.py
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


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user preferences and return reasons."""
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
    preferred_genres = user_prefs.get("genre", [])
    if not isinstance(preferred_genres, list):
        preferred_genres = [preferred_genres]

    if song.get("genre") in preferred_genres:
        score += 2.5
        reasons.append("genre match (+2.5)")

    # Rule 2: Mood match (max 2.0 points)
    preferred_moods = user_prefs.get("mood", [])
    if not isinstance(preferred_moods, list):
        preferred_moods = [preferred_moods]

    if song.get("mood") in preferred_moods:
        score += 2.0
        reasons.append("mood match (+2.0)")

    # Extract energy target and tolerance
    energy_prefs = user_prefs.get("energy", {})
    if isinstance(energy_prefs, dict):
        energy_target = energy_prefs.get("target", 0.30)
        energy_tolerance = energy_prefs.get("tolerance", 0.12)
    else:
        energy_target = 0.30
        energy_tolerance = 0.12

    # Rule 3: Energy similarity (max 2.0 points)
    if "energy" in song:
        energy_distance = abs(float(song["energy"]) - energy_target)
        energy_points = similarity(energy_distance, energy_tolerance, 2.0)
        if energy_points > 0:
            score += energy_points
            reasons.append(f"energy similarity (+{energy_points:.2f})")

    # Extract valence target and tolerance
    valence_prefs = user_prefs.get("valence", {})
    if isinstance(valence_prefs, dict):
        valence_target = valence_prefs.get("target", 0.60)
        valence_tolerance = valence_prefs.get("tolerance", 0.15)
    else:
        valence_target = 0.60
        valence_tolerance = 0.15

    # Rule 4: Valence similarity (max 1.5 points)
    if "valence" in song:
        valence_distance = abs(float(song["valence"]) - valence_target)
        valence_points = similarity(valence_distance, valence_tolerance, 1.5)
        if valence_points > 0:
            score += valence_points
            reasons.append(f"valence similarity (+{valence_points:.2f})")

    # Extract tempo target and tolerance
    tempo_prefs = user_prefs.get("tempo_bpm", {})
    if isinstance(tempo_prefs, dict):
        tempo_target = tempo_prefs.get("target", 82)
        tempo_tolerance = tempo_prefs.get("tolerance", 10)
    else:
        tempo_target = 82
        tempo_tolerance = 10

    # Rule 5: Tempo similarity (max 1.5 points)
    if "tempo_bpm" in song:
        tempo_distance = abs(float(song["tempo_bpm"]) - tempo_target)
        tempo_points = similarity(tempo_distance, tempo_tolerance, 1.5)
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

    # Clamp to [0, 10]
    final_score = min(10.0, max(0.0, score))

    return (final_score, reasons)


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Return top-k scored songs with a human-readable explanation string."""
    scored_songs = []

    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ". ".join(reasons) if reasons else "No matching criteria"
        scored_songs.append((song, score, explanation))

    # Sort by score descending, then return top k
    ranked = sorted(scored_songs, key=lambda x: x[1], reverse=True)
    return ranked[:k]
