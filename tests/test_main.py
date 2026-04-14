import ast
import subprocess
import sys
from pathlib import Path

from src import main as main_module


def test_main_defines_at_least_five_preference_presets():
    source = Path("src/main.py").read_text(encoding="utf-8")
    module = ast.parse(source)

    presets_node = None
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PREFERENCE_PRESETS":
                    presets_node = node.value
                    break

    assert isinstance(presets_node, ast.Dict)
    assert len(presets_node.keys) >= 5

    preset_names = [key.value for key in presets_node.keys if isinstance(key, ast.Constant)]
    assert len(preset_names) == len(set(preset_names))

    for value_node in presets_node.values:
        assert isinstance(value_node, ast.Dict)
        field_names = {
            key.value for key in value_node.keys if isinstance(key, ast.Constant)
        }
        assert {"genre", "mood", "energy"} <= field_names


def test_main_runs_all_presets_by_default(monkeypatch):
    called_profiles = []

    def fake_load_songs(_):
        return [{"title": "Mock Song", "genre": "pop", "mood": "happy", "energy": 0.8}]

    def fake_recommend_songs(user_prefs, songs, k):
        called_profiles.append(user_prefs)
        return [(songs[0], 1.0, "mock explanation")]

    monkeypatch.setattr(main_module, "load_songs", fake_load_songs)
    monkeypatch.setattr(main_module, "recommend_songs", fake_recommend_songs)

    main_module.main([])

    assert len(called_profiles) == len(main_module.PREFERENCE_PRESETS)


def test_main_runs_single_selected_preset(monkeypatch):
    called_profiles = []

    def fake_load_songs(_):
        return [{"title": "Mock Song", "genre": "pop", "mood": "happy", "energy": 0.8}]

    def fake_recommend_songs(user_prefs, songs, k):
        called_profiles.append(user_prefs)
        return [(songs[0], 1.0, "mock explanation")]

    monkeypatch.setattr(main_module, "load_songs", fake_load_songs)
    monkeypatch.setattr(main_module, "recommend_songs", fake_recommend_songs)

    main_module.main(["--preset", "Chill Lofi"])

    assert len(called_profiles) == 1
    assert called_profiles[0] == main_module.PREFERENCE_PRESETS["Chill Lofi"]


def test_main_script_entrypoint_runs_with_preset():
    result = subprocess.run(
        [sys.executable, "src/main.py", "--preset", "Chill Lofi", "--k", "1"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "=== Chill Lofi ===" in result.stdout


def test_presets_use_full_numeric_preference_schema():
    presets = main_module.PREFERENCE_PRESETS

    for profile in presets.values():
        assert isinstance(profile["genre"], str)
        assert isinstance(profile["mood"], str)
        for numeric_key in ("energy", "valence", "tempo_bpm"):
            assert numeric_key in profile
            assert isinstance(profile[numeric_key], dict)
            assert {"target", "tolerance"} <= set(profile[numeric_key].keys())


def test_main_outputs_structured_profile_block(monkeypatch, capsys):
    song = {
        "title": "Mock Song",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "artist": "Mock Artist",
    }

    def fake_load_songs(_):
        return [song]

    def fake_recommend_songs(user_prefs, songs, k):
        return [(songs[0], 9.12, "genre match (+2.50). mood match (+2.00)")]

    monkeypatch.setattr(main_module, "load_songs", fake_load_songs)
    monkeypatch.setattr(main_module, "recommend_songs", fake_recommend_songs)

    main_module.main(["--preset", "Chill Lofi", "--k", "1"])
    output = capsys.readouterr().out

    assert "=== Chill Lofi ===" in output
    assert "Preferences:" in output
    assert "#1 | Mock Song | score=9.12" in output
    assert "  - genre match (+2.50)" in output
    assert "  - mood match (+2.00)" in output
