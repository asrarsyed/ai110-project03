"""
Run basic fairness diagnostics across profile groups.
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.recommender import load_songs, recommend_songs


PROFILE_GROUPS = {
    "chill": {
        "genre": "lofi",
        "mood": "calm",
        "energy": {"target": 0.35, "tolerance": 0.12},
        "valence": {"target": 0.62, "tolerance": 0.15},
        "tempo_bpm": {"target": 78, "tolerance": 10},
    },
    "high-energy": {
        "genre": "pop",
        "mood": "happy",
        "energy": {"target": 0.90, "tolerance": 0.10},
        "valence": {"target": 0.80, "tolerance": 0.12},
        "tempo_bpm": {"target": 126, "tolerance": 10},
    },
    "mixed": {
        "genre": ["pop", "electronic"],
        "mood": ["happy", "moody"],
        "energy": {"target": 0.62, "tolerance": 0.18},
        "valence": {"target": 0.58, "tolerance": 0.18},
        "tempo_bpm": {"target": 110, "tolerance": 16},
    },
    "rare-label": {
        "genre": "drum & bass",
        "mood": "uplifted",
        "energy": {"target": 0.96, "tolerance": 0.08},
        "valence": {"target": 0.70, "tolerance": 0.12},
        "tempo_bpm": {"target": 172, "tolerance": 8},
    },
}


def run() -> None:
    songs = load_songs("data/songs.csv")
    averages = {}

    print("Fairness diagnostics")
    for group, prefs in PROFILE_GROUPS.items():
        results = recommend_songs(prefs, songs, k=5)
        avg_top5 = sum(score for _, score, _ in results) / len(results)
        averages[group] = avg_top5
        print(f"- {group}: average top-5 score = {avg_top5:.2f}")

    low_group = min(averages, key=averages.get)
    high_group = max(averages, key=averages.get)
    spread = averages[high_group] - averages[low_group]
    print()
    print(f"Score spread = {spread:.2f} ({low_group} -> {high_group})")
    if spread >= 1.5:
        print("Flag: high disparity detected; inspect alias coverage and tolerance settings.")
    else:
        print("Flag: disparity within moderate range.")


if __name__ == "__main__":
    run()
