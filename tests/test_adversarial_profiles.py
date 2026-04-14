import ast
from pathlib import Path


def test_adversarial_runner_defines_six_profiles():
    script_path = Path("notes/adversarial_profiles.py")
    assert script_path.exists()

    module = ast.parse(script_path.read_text(encoding="utf-8"))

    profiles_node = None
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ADVERSARIAL_PROFILES":
                    profiles_node = node.value
                    break

    assert isinstance(profiles_node, ast.Dict)
    assert len(profiles_node.keys) == 6
