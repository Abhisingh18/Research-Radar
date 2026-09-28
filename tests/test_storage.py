from pathlib import Path

from research_radar import storage


def test_load_seen_missing_file_returns_empty_set(tmp_path: Path):
    assert storage.load_seen(tmp_path / "does-not-exist.json") == set()


def test_save_and_load_round_trip(tmp_path: Path):
    state_file = tmp_path / "seen.json"
    storage.save_seen({"a", "b", "c"}, state_file)

    assert storage.load_seen(state_file) == {"a", "b", "c"}


def test_load_seen_ignores_corrupt_file(tmp_path: Path):
    state_file = tmp_path / "seen.json"
    state_file.write_text("not valid json", encoding="utf-8")

    assert storage.load_seen(state_file) == set()
