"""
Reusable adversarial profile runner for stress-testing recommender behavior.
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from recommender import load_songs, recommend_songs

ADVERSARIAL_PROFILES = {
    "Sad but Maximum Energy": {
        "genre": ["ambient"],
        "mood": ["sad"],
        "energy": {"target": 0.95, "tolerance": 0.05},
        "valence": {"target": 0.10, "tolerance": 0.08},
        "tempo_bpm": {"target": 70, "tolerance": 8},
    },
    "Calm Mood with DnB Tempo": {
        "genre": ["lofi"],
        "mood": ["chill"],
        "energy": {"target": 0.20, "tolerance": 0.06},
        "valence": {"target": 0.55, "tolerance": 0.10},
        "tempo_bpm": {"target": 175, "tolerance": 6},
    },
    "Ultra-Narrow Impossible Window": {
        "genre": ["folk"],
        "mood": ["intense"],
        "energy": {"target": 0.10, "tolerance": 0.01},
        "valence": {"target": 0.95, "tolerance": 0.01},
        "tempo_bpm": {"target": 150, "tolerance": 1},
    },
    "Out-of-Range Values": {
        "genre": ["pop"],
        "mood": ["happy"],
        "energy": {"target": 1.40, "tolerance": 0.20},
        "valence": {"target": -0.30, "tolerance": 0.20},
        "tempo_bpm": {"target": 260, "tolerance": 12},
    },
    "No Genre or Mood Signal": {
        "genre": [],
        "mood": [],
        "energy": {"target": 0.40, "tolerance": 0.15},
        "valence": {"target": 0.60, "tolerance": 0.20},
        "tempo_bpm": {"target": 90, "tolerance": 10},
    },
    "Everything-Preferred Category Spam": {
        "genre": [
            "pop",
            "rock",
            "lofi",
            "ambient",
            "metal",
            "folk",
            "jazz",
            "electronic",
            "house",
            "synthwave",
        ],
        "mood": ["happy", "chill", "intense", "focused", "moody", "relaxed"],
        "energy": {"target": 0.50, "tolerance": 0.50},
        "valence": {"target": 0.50, "tolerance": 0.50},
        "tempo_bpm": {"target": 110, "tolerance": 80},
    },
}


def run() -> None:
    songs = load_songs("data/songs.csv")

    for profile_name, prefs in ADVERSARIAL_PROFILES.items():
        print(f"\n=== {profile_name} ===")
        recommendations = recommend_songs(prefs, songs, k=5)
        for song, score, explanation in recommendations:
            print(f"- {song['title']} ({song['genre']}/{song['mood']}): {score:.2f}")
            print(f"  because: {explanation}")


if __name__ == "__main__":
    run()
