import subprocess


def run_osascript(body: str, *args: str) -> subprocess.CompletedProcess:
    """Run an AppleScript ``body`` passing ``args`` out-of-band via ``argv``.

    Data values must never be interpolated into AppleScript source: a single
    ``"`` or ``\\`` closes the string literal and lets the rest be parsed as
    code (``do shell script ...`` → RCE). Instead the values are handed to
    ``osascript`` as process arguments and read inside the script as
    ``item N of argv`` — quotes, backslashes and newlines pass through
    literally and can never be parsed as code (SEC-1).

    The ``body`` is wrapped in ``on run argv ... end run``; reference the
    passed values as ``item 1 of argv``, ``item 2 of argv`` ... in order.
    """
    script = f"on run argv\n{body}\nend run"
    return subprocess.run(
        ["osascript", "-e", script, *args],
        capture_output=True,
        text=True,
    )
