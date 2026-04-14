"""
Run controlled sensitivity experiments for the recommender.
"""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.main import PREFERENCE_PRESETS
from src.recommender import load_songs, recommend_songs


def _top5_map(results):
    return {song["id"]: (song["title"], score) for song, score, _ in results}


def run() -> None:
    songs = load_songs("data/songs.csv")
    profile_name = "High-Energy Pop"
    prefs = PREFERENCE_PRESETS[profile_name]

    baseline = recommend_songs(prefs, songs, k=5)
    weight_shift = recommend_songs(
        prefs,
        songs,
        k=5,
        score_config={"weights": {"genre": 0.5, "energy": 2.0}},
    )
    mood_off = recommend_songs(
        prefs,
        songs,
        k=5,
        score_config={"enable_mood": False},
    )

    baseline_ids = set(_top5_map(baseline))
    weight_ids = set(_top5_map(weight_shift))
    mood_off_ids = set(_top5_map(mood_off))

    print("Sensitivity experiments")
    print(f"Profile: {profile_name}")
    print()
    print(f"baseline top-5 IDs: {sorted(baseline_ids)}")
    print(f"weight-shift top-5 IDs: {sorted(weight_ids)}")
    print(f"mood-off top-5 IDs: {sorted(mood_off_ids)}")
    print()
    print(f"baseline vs weight-shift overlap: {len(baseline_ids & weight_ids)}/5")
    print(f"baseline vs mood-off overlap: {len(baseline_ids & mood_off_ids)}/5")
    print()
    print("Top-1 score deltas (vs baseline):")
    print(f"- weight-shift: {weight_shift[0][1] - baseline[0][1]:+.2f}")
    print(f"- mood-off: {mood_off[0][1] - baseline[0][1]:+.2f}")


if __name__ == "__main__":
    run()
