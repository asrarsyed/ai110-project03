from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    score_song,
    recommend_songs,
    _normalize_user_prefs,
    _profile_reliability,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_normalize_user_prefs_clamps_targets_and_tolerances():
    prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": {"target": 1.4, "tolerance": 9.0},
        "valence": {"target": -0.3, "tolerance": 4.0},
        "tempo_bpm": {"target": 260, "tolerance": 80},
    }

    normalized = _normalize_user_prefs(prefs)
    assert normalized["energy"]["target"] == 1.0
    assert normalized["energy"]["tolerance"] == 0.25
    assert normalized["valence"]["target"] == 0.0
    assert normalized["valence"]["tolerance"] == 0.25
    assert normalized["tempo_bpm"]["target"] == 220
    assert normalized["tempo_bpm"]["tolerance"] == 25


def test_category_spam_gets_less_weight_than_focused_preferences():
    song = {
        "id": 99,
        "title": "Control Track",
        "artist": "Unit Test",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.50,
        "tempo_bpm": 110,
        "valence": 0.50,
        "danceability": 0.5,
        "acousticness": 0.2,
    }
    focused_prefs = {
        "genre": ["pop"],
        "mood": ["happy"],
        "energy": {"target": 0.50, "tolerance": 0.20},
        "valence": {"target": 0.50, "tolerance": 0.20},
        "tempo_bpm": {"target": 110, "tolerance": 20},
    }
    spammy_prefs = {
        "genre": ["pop", "rock", "lofi", "house", "ambient", "metal", "jazz"],
        "mood": ["happy", "chill", "intense", "moody", "relaxed", "focused"],
        "energy": {"target": 0.50, "tolerance": 0.20},
        "valence": {"target": 0.50, "tolerance": 0.20},
        "tempo_bpm": {"target": 110, "tolerance": 20},
    }

    focused_score, _ = score_song(focused_prefs, song)
    spammy_score, _ = score_song(spammy_prefs, song)

    assert spammy_score < focused_score


def test_no_genre_or_mood_signal_caps_score():
    song = {
        "id": 100,
        "title": "Numeric Match Track",
        "artist": "Unit Test",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.40,
        "tempo_bpm": 90,
        "valence": 0.60,
        "danceability": 0.5,
        "acousticness": 0.2,
    }
    prefs = {
        "genre": [],
        "mood": [],
        "energy": {"target": 0.40, "tolerance": 0.20},
        "valence": {"target": 0.60, "tolerance": 0.20},
        "tempo_bpm": {"target": 90, "tolerance": 20},
    }
    score, _ = score_song(prefs, song)
    assert score <= 6.0


def test_tie_break_prefers_closer_numeric_match():
    prefs = {
        "genre": ["pop"],
        "mood": ["happy"],
        "energy": {"target": 0.50, "tolerance": 0.50},
        "valence": {"target": 0.50, "tolerance": 0.50},
        "tempo_bpm": {"target": 100, "tolerance": 80},
    }
    songs = [
        {
            "id": 1,
            "title": "Closer Match",
            "artist": "Unit Test",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.52,
            "tempo_bpm": 102,
            "valence": 0.52,
            "danceability": 0.5,
            "acousticness": 0.2,
        },
        {
            "id": 2,
            "title": "Farther Match",
            "artist": "Unit Test",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.95,
            "tempo_bpm": 130,
            "valence": 0.95,
            "danceability": 0.5,
            "acousticness": 0.2,
        },
    ]

    ranked = recommend_songs(prefs, songs, k=2)
    assert ranked[0][0]["title"] == "Closer Match"
    assert ranked[1][0]["title"] == "Farther Match"


def test_conflicting_profile_has_lower_reliability():
    conflicting = {
        "genre": ["ambient"],
        "mood": ["sad", "chill"],
        "energy": {"target": 0.95, "tolerance": 0.08},
        "valence": {"target": 0.90, "tolerance": 0.10},
        "tempo_bpm": {"target": 70, "tolerance": 10},
    }
    coherent = {
        "genre": ["rock"],
        "mood": ["intense", "energetic"],
        "energy": {"target": 0.90, "tolerance": 0.12},
        "valence": {"target": 0.70, "tolerance": 0.10},
        "tempo_bpm": {"target": 160, "tolerance": 12},
    }

    assert _profile_reliability(conflicting) < _profile_reliability(coherent)


def test_alias_matching_handles_edm_and_calm_labels():
    song = {
        "id": 501,
        "title": "Alias Match Song",
        "artist": "Unit Test",
        "genre": "electronic",
        "mood": "chill",
        "energy": 0.85,
        "tempo_bpm": 128,
        "valence": 0.75,
        "danceability": 0.8,
        "acousticness": 0.1,
    }
    prefs = {
        "genre": "edm",
        "mood": "calm",
        "energy": {"target": 0.85, "tolerance": 0.10},
        "valence": {"target": 0.75, "tolerance": 0.10},
        "tempo_bpm": {"target": 128, "tolerance": 10},
    }

    score, reasons = score_song(prefs, song)
    assert score > 0
    assert any("genre match" in reason for reason in reasons)
    assert any("mood match" in reason for reason in reasons)


def test_diversity_reranker_reduces_artist_repetition_in_top_k():
    prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": {"target": 0.85, "tolerance": 0.20},
        "valence": {"target": 0.80, "tolerance": 0.20},
        "tempo_bpm": {"target": 122, "tolerance": 15},
    }
    songs = [
        {
            "id": 601,
            "title": "Artist A Track 1",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.86,
            "tempo_bpm": 121,
            "valence": 0.82,
            "danceability": 0.8,
            "acousticness": 0.2,
        },
        {
            "id": 602,
            "title": "Artist A Track 2",
            "artist": "Artist A",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.85,
            "tempo_bpm": 122,
            "valence": 0.81,
            "danceability": 0.8,
            "acousticness": 0.2,
        },
        {
            "id": 603,
            "title": "Artist B Track",
            "artist": "Artist B",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.83,
            "tempo_bpm": 120,
            "valence": 0.79,
            "danceability": 0.8,
            "acousticness": 0.2,
        },
    ]

    ranked = recommend_songs(prefs, songs, k=3)
    top_two_artists = [ranked[0][0]["artist"], ranked[1][0]["artist"]]
    assert len(set(top_two_artists)) == 2
