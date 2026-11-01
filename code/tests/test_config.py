from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _leaf_keys(node, prefix=()):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _leaf_keys(value, prefix + (str(key),))
    else:
        yield prefix[-1]


def test_every_base_config_key_is_read_by_the_code():
    base = yaml.safe_load((ROOT / "configs" / "base.yaml").read_text(encoding="utf-8"))
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "src").glob("*.py"))
    for key in _leaf_keys(base):
        assert f'"{key}"' in source, f"config key {key!r} is never read"


def test_experiment_config_keys_are_read_by_the_code():
    experiments = yaml.safe_load((ROOT / "configs" / "experiments.yaml").read_text(encoding="utf-8"))
    source = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "src").glob("*.py"))
    for name, config in experiments["experiments"].items():
        for key in config:
            if key in {"name", "priority", "noise", "graphs", "marked", "cue", "targets", "cases"}:
                continue
            assert f'"{key}"' in source, f"{name}: config key {key!r} is never read"
