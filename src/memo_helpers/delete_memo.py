import click
from memo_helpers.run_osascript import run_osascript


def delete_note(note_id):
    script = """
    set theNoteId to item 1 of argv
    tell application "Notes"
        set theNote to first note whose id is theNoteId
        delete theNote
    end tell
    """

    result = run_osascript(script, note_id)

    if result.returncode == 0:
        click.secho("\nNote deleted successfully.", fg="green")
    else:
        click.secho(f"Error: {result.stderr}", fg="red")


def delete_note_folder(folder_name):
    script = """
    set theFolderName to item 1 of argv
    tell application "Notes"
        set selectedFolder to first folder whose name is theFolderName
        delete selectedFolder
    end tell
    """
    result = run_osascript(script, folder_name)

    if result.returncode == 0:
        click.secho("\nFolder deleted successfully.", fg="green")
    else:
        click.secho(f"Error: {result.stderr}", fg="red")


def complete_reminder(reminder_id):
    script = """
        set theReminderId to item 1 of argv
        tell application "Reminders"
            set selectedRem to first reminder whose id is theReminderId
            set completed of selectedRem to true
        end tell
        """

    result = run_osascript(script, reminder_id)

    if result.returncode == 0:
        click.secho("\nReminder marked successfully as completed.", fg="green")
    else:
        click.secho(f"Error: {result.stderr}", fg="red")


def delete_reminder(reminder_id):
    script = """
        set theReminderId to item 1 of argv
        tell application "Reminders"
        set selectedRem to first reminder whose id is theReminderId
        delete selectedRem
    end tell
    """
    result = run_osascript(script, reminder_id)

    if result.returncode == 0:
        click.secho("\nReminder deleted successfully.", fg="green")
    else:
        click.secho(f"Error: {result.stderr}", fg="red")
