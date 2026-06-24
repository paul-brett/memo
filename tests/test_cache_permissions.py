import os
import stat

import pytest

from memo_helpers import cache_memo


@pytest.fixture
def patched_cache(tmp_path, monkeypatch):
    cache_dir = tmp_path / "memo"
    cache_file = cache_dir / "notes_cache.json"
    monkeypatch.setattr(cache_memo, "CACHE_DIR", str(cache_dir))
    monkeypatch.setattr(cache_memo, "CACHE_FILE", str(cache_file))
    return cache_dir, cache_file


def _mode(path):
    return stat.S_IMODE(os.stat(path).st_mode)


@pytest.mark.skipif(
    os.name == "nt", reason="POSIX permissions not applicable on Windows"
)
def test_save_cache_sets_owner_only_perms(patched_cache):
    cache_dir, cache_file = patched_cache
    cache_memo.save_cache({1: ("Title", "Folder")}, ["Title"])
    assert _mode(cache_file) == 0o600
    assert _mode(cache_dir) == 0o700


@pytest.mark.skipif(
    os.name == "nt", reason="POSIX permissions not applicable on Windows"
)
def test_save_cache_tightens_existing_loose_dir_and_file(patched_cache):
    cache_dir, cache_file = patched_cache
    # Pre-existing dir and file with loose, world-readable perms.
    os.makedirs(cache_dir, mode=0o755)
    os.chmod(cache_dir, 0o755)
    cache_file.write_text("{}")
    os.chmod(cache_file, 0o644)
    assert _mode(cache_dir) == 0o755
    assert _mode(cache_file) == 0o644

    cache_memo.save_cache({1: ("Title", "Folder")}, ["Title"])

    assert _mode(cache_dir) == 0o700
    assert _mode(cache_file) == 0o600
