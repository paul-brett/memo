"""Regression tests for SEC-2: edit_note leaks note content to a temp file.

``edit_note`` writes the (decrypted) note to a ``NamedTemporaryFile(
delete=False)`` and must remove it on *every* exit path — success, the
no-changes early return, and the update-failed early return — so a plaintext
copy of the note is not left behind on disk.

The tests let the real temp file be created, capture its path, mock the editor
and osascript boundaries, then assert the file no longer exists after
``edit_note`` returns.
"""

import os
from unittest.mock import patch, MagicMock


def _run_edit_note(edited_text, *, returncode=0):
    """Run edit_note with a real temp file; return the temp path it used."""
    from memo_helpers import edit_memo

    captured = {}

    def fake_editor(args, *a, **k):
        # args == [editor, temp_path]; record the path the temp file lives at.
        captured["path"] = args[1]
        # Simulate the user's edit by writing edited_text into the temp file.
        with open(args[1], "w", encoding="utf-8") as f:
            f.write(edited_text)
        return MagicMock(returncode=0)

    with (
        patch.object(edit_memo, "id_search_memo", return_value=MagicMock()),
        patch.object(
            edit_memo, "md_converter", return_value=("original md", "<html>", {})
        ),
        patch.object(edit_memo.subprocess, "run", side_effect=fake_editor),
        patch.object(edit_memo.os, "getenv", return_value="true"),
        patch.object(
            edit_memo,
            "run_osascript",
            return_value=MagicMock(returncode=returncode, stdout="", stderr=""),
        ),
    ):
        edit_memo.edit_note("note-id")

    return captured["path"]


def test_tempfile_removed_on_success():
    path = _run_edit_note("edited md")  # differs -> update path, rc=0
    assert path is not None
    assert not os.path.exists(path), "temp file leaked on the success path"


def test_tempfile_removed_when_no_changes():
    path = _run_edit_note("original md")  # identical -> "No changes" early return
    assert path is not None
    assert not os.path.exists(path), "temp file leaked on the no-changes path"


def test_tempfile_removed_when_update_fails():
    path = _run_edit_note("edited md", returncode=1)  # update fails early return
    assert path is not None
    assert not os.path.exists(path), "temp file leaked on the update-failed path"
