import click
from memo_helpers.run_osascript import run_osascript


def move_note(note_id: str, target_folder: str):

    script = """
    set theNoteId to item 1 of argv
    set theTargetFolder to item 2 of argv
    tell application "Notes"
        set noteToMove to missing value
        set noteName to ""
        set noteBody to ""
        set accToUse to missing value
        repeat with acc in accounts
            repeat with f in folders of acc
                try
                    set n to first note of f whose id is theNoteId
                    set noteToMove to n
                    set noteName to name of n
                    set noteBody to body of n
                    set accToUse to acc
                    exit repeat
                end try
            end repeat
            if noteToMove is not missing value then exit repeat
        end repeat
        if noteToMove is not missing value then
            set destinationFolder to missing value
            try
                set destinationFolder to folder theTargetFolder of accToUse
            on error
                set destinationFolder to make new folder with properties {name:theTargetFolder} at accToUse
            end try
            make new note at destinationFolder with properties {name:noteName, body:noteBody}
            delete noteToMove
        end if
    end tell
    """
    result = run_osascript(script, note_id, target_folder)
    if result.returncode == 0:
        click.secho(f'\n✅ The note was moved to "{target_folder}" folder.', fg="green")
    else:
        click.secho(f"\n❌ Error while moving: {result.stderr}", fg="red")
