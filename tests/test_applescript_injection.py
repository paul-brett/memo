"""Regression tests for SEC-1: AppleScript injection via string interpolation.

Every value that originates from user/note/folder data must reach ``osascript``
as a discrete ``argv`` element, never interpolated into the script source. These
tests feed quote/backslash/newline payloads (and a ``do shell script`` RCE
payload) through each sink and assert the payload is passed as a separate
argument and never appears as a substring of the script body (``args[0]`` of the
osascript invocation after ``-e SCRIPT``).
"""

from unittest.mock import patch, MagicMock

from memo_helpers.run_osascript import run_osascript

# A payload that breaks naive f-string interpolation and attempts RCE.
PAYLOAD = 'evil" \\ \n do shell script "touch /tmp/INJECTED" --'


def _osascript_call(mock_run):
    """Return (script, extra_args) from the osascript subprocess call."""
    args = mock_run.call_args.args[0]
    assert args[0] == "osascript"
    assert args[1] == "-e"
    script = args[2]
    # Everything after the script is the data passed via argv.
    extra = args[3:]
    return script, extra


def _assert_payload_isolated(script, extra):
    assert PAYLOAD not in script, "payload was interpolated into the script source"
    assert PAYLOAD in extra, "payload was not passed as a discrete argv element"


# --- The central helper ------------------------------------------------------


@patch("memo_helpers.run_osascript.subprocess.run")
def test_run_osascript_passes_args_via_argv(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    run_osascript("return item 1 of argv", PAYLOAD)
    script, extra = _osascript_call(mock_run)
    assert script.startswith("on run argv")
    assert script.rstrip().endswith("end run")
    _assert_payload_isolated(script, extra)


# --- add_memo ----------------------------------------------------------------


@patch("memo_helpers.add_memo.run_osascript")
@patch("memo_helpers.add_memo.subprocess.run")
@patch("memo_helpers.add_memo.os.remove")
@patch("memo_helpers.add_memo.open")
@patch("memo_helpers.add_memo.mistune.markdown")
def test_add_note_payload_via_argv(
    mock_md, mock_open, mock_remove, mock_subproc, mock_run
):
    from memo_helpers.add_memo import add_note

    mock_md.return_value = PAYLOAD  # the note body (html)
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    # Make the editor read return a non-cancel body.
    handle = MagicMock()
    handle.read.return_value = "some note"
    mock_open.return_value.__enter__.return_value = handle

    add_note(PAYLOAD)  # folder_name is also a payload

    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


@patch("memo_helpers.add_memo.run_osascript")
@patch("memo_helpers.add_memo.click.prompt")
def test_add_reminder_title_via_argv(mock_prompt, mock_run):
    from memo_helpers.add_memo import add_reminder

    mock_prompt.side_effect = [PAYLOAD, "2099-12-31", "12:00"]
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    add_reminder()

    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


# --- delete_memo -------------------------------------------------------------


@patch("memo_helpers.delete_memo.run_osascript")
def test_delete_note_id_via_argv(mock_run):
    from memo_helpers.delete_memo import delete_note

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    delete_note(PAYLOAD)
    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


@patch("memo_helpers.delete_memo.run_osascript")
def test_delete_note_folder_via_argv(mock_run):
    from memo_helpers.delete_memo import delete_note_folder

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    delete_note_folder(PAYLOAD)
    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


@patch("memo_helpers.delete_memo.run_osascript")
def test_complete_reminder_via_argv(mock_run):
    from memo_helpers.delete_memo import complete_reminder

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    complete_reminder(PAYLOAD)
    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


@patch("memo_helpers.delete_memo.run_osascript")
def test_delete_reminder_via_argv(mock_run):
    from memo_helpers.delete_memo import delete_reminder

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    delete_reminder(PAYLOAD)
    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


# --- move_memo ---------------------------------------------------------------


@patch("memo_helpers.move_memo.run_osascript")
def test_move_note_via_argv(mock_run):
    from memo_helpers.move_memo import move_note

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    move_note(PAYLOAD, PAYLOAD)
    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


# --- id_search_memo ----------------------------------------------------------


@patch("memo_helpers.id_search_memo.run_osascript")
def test_id_search_via_argv(mock_run):
    from memo_helpers.id_search_memo import id_search_memo

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    id_search_memo(PAYLOAD)
    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


# --- export_memo -------------------------------------------------------------


@patch("memo_helpers.export_memo.click.confirm", return_value=False)
@patch("memo_helpers.export_memo.run_osascript")
def test_export_path_and_folder_via_argv(mock_run, mock_confirm):
    from memo_helpers.export_memo import export_memo

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    export_memo(PAYLOAD, PAYLOAD)
    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


# --- edit_memo ---------------------------------------------------------------


@patch("memo_helpers.edit_memo.run_osascript")
@patch("memo_helpers.edit_memo.click.prompt")
def test_edit_reminder_title_via_argv(mock_prompt, mock_run):
    from memo_helpers.edit_memo import edit_reminder

    mock_prompt.return_value = PAYLOAD
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    edit_reminder(PAYLOAD, "title")
    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


@patch("memo_helpers.edit_memo.run_osascript")
@patch("memo_helpers.edit_memo.os.getenv")
@patch("memo_helpers.edit_memo.subprocess.run")
@patch("memo_helpers.edit_memo.open")
@patch("memo_helpers.edit_memo.mistune.markdown")
@patch("memo_helpers.edit_memo.md_converter")
@patch("memo_helpers.edit_memo.id_search_memo")
def test_edit_note_body_and_id_via_argv(
    mock_id_search,
    mock_converter,
    mock_md,
    mock_open,
    mock_subproc,
    mock_getenv,
    mock_run,
):
    from memo_helpers.edit_memo import edit_note

    mock_id_search.return_value = MagicMock()
    mock_converter.return_value = ("original md", "<html>", {})
    mock_getenv.return_value = "true"
    handle = MagicMock()
    handle.read.return_value = "edited md"  # differs from original -> proceeds
    mock_open.return_value.__enter__.return_value = handle
    mock_md.return_value = PAYLOAD  # edited_html
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    edit_note(PAYLOAD)  # note_id is also a payload

    script = mock_run.call_args.args[0]
    extra = mock_run.call_args.args[1:]
    assert PAYLOAD not in script
    assert PAYLOAD in extra


# --- argv ordering -----------------------------------------------------------
# Reusing one payload for every argument can't catch a transposed
# item 1/item 2. These feed distinct values per position and assert order.

ARG1 = "first-arg-VALUE-1"
ARG2 = "second-arg-VALUE-2"


@patch("memo_helpers.move_memo.run_osascript")
def test_move_note_arg_order(mock_run):
    from memo_helpers.move_memo import move_note

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    move_note(ARG1, ARG2)  # note_id, target_folder
    extra = mock_run.call_args.args[1:]
    assert extra == (ARG1, ARG2)


@patch("memo_helpers.add_memo.run_osascript")
@patch("memo_helpers.add_memo.subprocess.run")
@patch("memo_helpers.add_memo.os.remove")
@patch("memo_helpers.add_memo.open")
@patch("memo_helpers.add_memo.mistune.markdown")
def test_add_note_arg_order(mock_md, mock_open, mock_remove, mock_subproc, mock_run):
    from memo_helpers.add_memo import add_note

    mock_md.return_value = ARG2  # note body (html) -> item 2
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    handle = MagicMock()
    handle.read.return_value = "some note"
    mock_open.return_value.__enter__.return_value = handle

    add_note(ARG1)  # folder_name -> item 1
    extra = mock_run.call_args.args[1:]
    assert extra == (ARG1, ARG2)


@patch("memo_helpers.export_memo.click.confirm", return_value=False)
@patch("memo_helpers.export_memo.run_osascript")
def test_export_arg_order(mock_run, mock_confirm):
    from memo_helpers.export_memo import export_memo

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    export_memo(ARG1, ARG2)  # path -> item 1, notes_folder -> item 2
    extra = mock_run.call_args.args[1:]
    assert extra == (ARG1, ARG2)


@patch("memo_helpers.export_memo.click.confirm", return_value=False)
@patch("memo_helpers.export_memo.run_osascript")
def test_export_no_folder_passes_empty_string(mock_run, mock_confirm):
    from memo_helpers.export_memo import export_memo

    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    export_memo(ARG1)  # notes_folder defaults to None -> "" arg
    extra = mock_run.call_args.args[1:]
    assert extra == (ARG1, "")


@patch("memo_helpers.edit_memo.run_osascript")
@patch("memo_helpers.edit_memo.os.getenv")
@patch("memo_helpers.edit_memo.subprocess.run")
@patch("memo_helpers.edit_memo.open")
@patch("memo_helpers.edit_memo.mistune.markdown")
@patch("memo_helpers.edit_memo.md_converter")
@patch("memo_helpers.edit_memo.id_search_memo")
def test_edit_note_arg_order(
    mock_id_search,
    mock_converter,
    mock_md,
    mock_open,
    mock_subproc,
    mock_getenv,
    mock_run,
):
    from memo_helpers.edit_memo import edit_note

    mock_id_search.return_value = MagicMock()
    mock_converter.return_value = ("original md", "<html>", {})
    mock_getenv.return_value = "true"
    handle = MagicMock()
    handle.read.return_value = "edited md"
    mock_open.return_value.__enter__.return_value = handle
    mock_md.return_value = ARG2  # edited_html -> item 2
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    edit_note(ARG1)  # note_id -> item 1
    extra = mock_run.call_args.args[1:]
    assert extra == (ARG1, ARG2)


@patch("memo_helpers.edit_memo.run_osascript")
@patch("memo_helpers.edit_memo.click.prompt")
def test_edit_reminder_title_arg_order(mock_prompt, mock_run):
    from memo_helpers.edit_memo import edit_reminder

    mock_prompt.return_value = ARG2  # new title -> item 2
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
    edit_reminder(ARG1, "title")  # reminder_id -> item 1
    extra = mock_run.call_args.args[1:]
    assert extra == (ARG1, ARG2)
