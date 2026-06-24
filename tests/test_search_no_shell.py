from unittest.mock import patch

from memo_helpers.search_memo import fuzzy_notes

FAKE_NOTE_ID = "x-coredata://fake-id-123"
FAKE_NOTE_TITLE = "My Folder - Test Note"
FAKE_NOTE_MAP = {1: (FAKE_NOTE_ID, FAKE_NOTE_TITLE)}
FAKE_NOTES_LIST = [FAKE_NOTE_TITLE]


@patch("memo_helpers.search_memo.subprocess.run")
@patch("memo_helpers.search_memo.md_converter")
@patch("memo_helpers.search_memo.id_search_memo")
@patch("memo_helpers.search_memo.get_note")
def test_fuzzy_notes_invokes_fzf_without_shell(
    mock_get_note, mock_id_search, mock_md_converter, mock_run
):
    mock_get_note.return_value = [FAKE_NOTE_MAP, FAKE_NOTES_LIST]
    mock_id_search.return_value = "<div>content</div>"
    mock_md_converter.return_value = ["# content"]

    fuzzy_notes()

    assert mock_run.called
    args, kwargs = mock_run.call_args

    # First positional arg must be a list (arg vector), not a shell string.
    command = args[0]
    assert isinstance(command, list), f"expected list, got {type(command)}"

    # shell=True must not be used.
    assert kwargs.get("shell") is not True

    # The arg vector must start with fzf.
    assert command[0] == "fzf"

    # The stray demo binding must be gone.
    assert not any("git ls-files" in element for element in command)
