"""
Tmux controller: single abstraction over tmux CLI.
Handlers must use this module only; they must not call tmux directly.

Output capture is limited to MAX_CAPTURE_LINES to avoid exceeding Telegram message size.
Truncation is applied when returning captured output (see capture_pane).
"""

import subprocess
import shutil
from typing import Optional

# Max lines to capture from tmux pane. Telegram message limit ~4096 chars; we limit by lines.
MAX_CAPTURE_LINES = 200
TRUNCATED_SUFFIX = "\n... (truncated)"


def _tmux(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run tmux with given args. Raises if tmux not found or exits non-zero when check=True."""
    exe = shutil.which("tmux")
    if not exe:
        raise RuntimeError("tmux not found in PATH")
    return subprocess.run(
        [exe] + args,
        capture_output=True,
        text=True,
        timeout=30,
        check=check,
    )


def session_exists(session_name: str) -> bool:
    """Return True if a tmux session with this name exists."""
    r = _tmux(["has-session", "-t", session_name], check=False)
    return r.returncode == 0


def create_session(session_name: str, working_directory: Optional[str] = None) -> None:
    """Create a new tmux session. Fails if session already exists."""
    args = ["new-session", "-d", "-s", session_name]
    if working_directory:
        args.extend(["-c", working_directory])
    _tmux(args)


def send_keys(session_name: str, keys: str, enter: bool = True) -> None:
    """Send keys to the session's pane. If enter=True, append Enter."""
    args = ["send-keys", "-t", session_name, keys]
    if enter:
        args.append("Enter")
    _tmux(args)


def send_ctrl_c(session_name: str) -> None:
    """Send Ctrl+C to the session's pane."""
    _tmux(["send-keys", "-t", session_name, "C-c"])


def capture_pane(
    session_name: str,
    lines: int = 50,
    max_lines: int = MAX_CAPTURE_LINES,
) -> str:
    """
    Capture the last `lines` lines from the session's pane.
    Result is truncated to `max_lines` with TRUNCATED_SUFFIX if larger.
    """
    if lines <= 0 or lines > max_lines:
        lines = min(max_lines, 50)
    # -S -N: start N lines above bottom; -p: print to stdout
    r = _tmux(["capture-pane", "-t", session_name, "-p", "-S", f"-{lines}"])
    out = (r.stdout or "").rstrip()
    line_count = out.count("\n") + 1 if out else 0
    if line_count > max_lines:
        truncated = "\n".join(out.split("\n")[-max_lines:])
        out = truncated + TRUNCATED_SUFFIX
    return out


def kill_session(session_name: str) -> None:
    """Kill the tmux session. No-op if the session does not exist (idempotent)."""
    r = _tmux(["kill-session", "-t", session_name], check=False)
    if r.returncode != 0:
        # Exit 1 = session not found; treat as success (already gone).
        if r.returncode != 1:
            raise subprocess.CalledProcessError(r.returncode, [shutil.which("tmux"), "kill-session", "-t", session_name], r.stdout, r.stderr)


def clear_pane(session_name: str) -> None:
    """Clear the terminal (send 'clear' command to the pane)."""
    send_keys(session_name, "clear", enter=True)


def rename_session(old_name: str, new_name: str) -> None:
    """Rename a tmux session."""
    _tmux(["rename-session", "-t", old_name, new_name])


def get_session_cwd(session_name: str) -> Optional[str]:
    """
    Return the current working directory of the session's pane.
    Uses tmux display-message to get pane_current_path.
    Returns None if session does not exist or path cannot be determined.
    """
    r = _tmux(
        ["display-message", "-t", session_name, "-p", "#{pane_current_path}"],
        check=False,
    )
    if r.returncode != 0:
        return None
    path = (r.stdout or "").strip()
    return path if path else None
