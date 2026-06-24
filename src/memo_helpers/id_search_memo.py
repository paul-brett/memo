from memo_helpers.run_osascript import run_osascript


def id_search_memo(note_id):
    script = """
        set theNoteId to item 1 of argv
        tell application "Notes"
            set selectedNote to first note whose id is theNoteId
            return body of selectedNote
        end tell
        """
    return run_osascript(script, note_id)
