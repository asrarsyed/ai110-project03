"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from recommender import load_songs, recommend_songs
else:
    from src.recommender import load_songs, recommend_songs

PREFERENCE_PRESETS = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": {"target": 0.88, "tolerance": 0.12},
        "valence": {"target": 0.82, "tolerance": 0.15},
        "tempo_bpm": {"target": 124, "tolerance": 12},
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "calm",
        "energy": {"target": 0.38, "tolerance": 0.10},
        "valence": {"target": 0.58, "tolerance": 0.14},
        "tempo_bpm": {"target": 78, "tolerance": 10},
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": {"target": 0.94, "tolerance": 0.08},
        "valence": {"target": 0.46, "tolerance": 0.12},
        "tempo_bpm": {"target": 150, "tolerance": 14},
    },
    "Upbeat Dance": {
        "genre": "edm",
        "mood": "excited",
        "energy": {"target": 0.86, "tolerance": 0.12},
        "valence": {"target": 0.76, "tolerance": 0.14},
        "tempo_bpm": {"target": 128, "tolerance": 10},
    },
    "Soft Acoustic Calm": {
        "genre": "acoustic",
        "mood": "relaxed",
        "energy": {"target": 0.30, "tolerance": 0.10},
        "valence": {"target": 0.66, "tolerance": 0.14},
        "tempo_bpm": {"target": 86, "tolerance": 10},
    },
}


def _profile_summary(user_prefs: Dict) -> str:
    energy = user_prefs.get("energy", {})
    valence = user_prefs.get("valence", {})
    tempo = user_prefs.get("tempo_bpm", {})
    return (
        f"genre={user_prefs.get('genre')} | mood={user_prefs.get('mood')} | "
        f"energy={energy.get('target')}±{energy.get('tolerance')} | "
        f"valence={valence.get('target')}±{valence.get('tolerance')} | "
        f"tempo={tempo.get('target')}±{tempo.get('tolerance')}"
    )


def _reason_items(explanation: str) -> List[str]:
    return [item.strip() for item in explanation.split(". ") if item.strip()]


def _run_profile(profile_name: str, user_prefs: Dict, songs: List[Dict], k: int) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print(f"\n=== {profile_name} ===\n")
    print(f"Preferences: {_profile_summary(user_prefs)}")
    print()
    for index, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"#{index} | {song['title']} | score={score:.2f}")
        for reason in _reason_items(explanation):
            print(f"  - {reason}")
        print()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run music recommendations by preset.")
    parser.add_argument(
        "--preset",
        choices=sorted(PREFERENCE_PRESETS.keys()),
        help="Run recommendations for one named preset. Omit to run all presets.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of recommendations per profile (default: 5).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.k <= 0:
        parser.error("--k must be a positive integer.")

    songs = load_songs("data/songs.csv")
    if args.preset:
        selected_profiles: Iterable[Tuple[str, Dict]] = [
            (args.preset, PREFERENCE_PRESETS[args.preset])
        ]
    else:
        selected_profiles = PREFERENCE_PRESETS.items()

    for profile_name, user_prefs in selected_profiles:
        _run_profile(profile_name, user_prefs, songs, args.k)


if __name__ == "__main__":
    main()
