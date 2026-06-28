import os
import shutil
from pathlib import Path
from typing import Dict, Iterable, List, Optional

APP_EXTENSIONS = {'.lnk', '.url', '.exe', '.appref-ms', '.msc', '.bat', '.ps1'}
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    'Browsers': ['chrome', 'edge', 'firefox', 'brave', 'opera', 'browser', 'internet explorer', 'iexplore'],
    'Productivity': ['word', 'excel', 'powerpoint', 'onenote', 'outlook', 'vscode', 'code', 'notepad', 'slack', 'notion', 'todo'],
    'Communication': ['teams', 'zoom', 'discord', 'skype', 'signal', 'whatsapp', 'telegram', 'messenger'],
    'Games': ['steam', 'epic', 'gog', 'battle.net', 'origin', 'launcher', 'game', 'minecraft'],
    'Development': ['pycharm', 'intellij', 'android studio', 'git', 'docker', 'node', 'python', 'ruby', 'java', 'vscode'],
    'Utilities': ['settings', 'control panel', 'cmd', 'powershell', 'terminal', 'run', 'explorer', 'task manager', 'disk', 'network', 'system'],
}
DEFAULT_CATEGORY = 'Unsorted'


def organizer_py(path: Optional[str] = None, dry_run: bool = False) -> Dict[str, int]:
    """Organize desktop app shortcuts and executables in the target path."""
    return organize_desktop(path, dry_run=dry_run)


def get_desktop_path() -> Path:
    """Return a best-effort path to the current user's Desktop."""
    home = os.environ.get('USERPROFILE') or os.environ.get('HOME')
    if not home:
        raise RuntimeError('Unable to locate user home directory for Desktop lookup.')
    return Path(home) / 'Desktop'


def categorize_item(path: Path) -> str:
    """Choose a category for a desktop item using keywords and extension heuristics."""
    name = path.stem.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in name for keyword in keywords):
            return category
    return DEFAULT_CATEGORY


def ensure_folder(path: Path) -> Path:
    """Create the destination folder if it does not exist."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    return path


def unique_destination(target: Path) -> Path:
    """Return a unique destination path when the target already exists."""
    if not target.exists():
        return target
    base = target.stem
    suffix = target.suffix
    counter = 1
    while True:
        candidate = target.with_name(f'{base} ({counter}){suffix}')
        if not candidate.exists():
            return candidate
        counter += 1


def move_item(source: Path, destination_dir: Path, dry_run: bool = False) -> Path:
    """Move a single item to the destination folder, optionally in dry-run mode."""
    destination_dir = ensure_folder(destination_dir)
    destination = destination_dir / source.name
    destination = unique_destination(destination)
    if dry_run:
        return destination
    return Path(shutil.move(str(source), str(destination)))


def organize_desktop(path: Optional[str] = None, dry_run: bool = False, only_app_shortcuts: bool = True) -> Dict[str, int]:
    """Organize desktop items into category folders and return a summary count."""
    base_dir = Path(path) if path else get_desktop_path()
    base_dir = base_dir.expanduser().resolve()
    if not base_dir.exists() or not base_dir.is_dir():
        raise ValueError(f'Path does not exist or is not a directory: {base_dir}')

    summary: Dict[str, int] = {}
    for entry in base_dir.iterdir():
        if entry.is_dir():
            continue
        suffix = entry.suffix.lower()
        if only_app_shortcuts and suffix not in APP_EXTENSIONS:
            continue
        category = categorize_item(entry)
        destination_dir = base_dir / category
        if destination_dir == entry.parent:
            continue
        move_item(entry, destination_dir, dry_run=dry_run)
        summary[category] = summary.get(category, 0) + 1

    return summary


def list_categories() -> Iterable[str]:
    """Return the names of the available desktop app categories."""
    return list(CATEGORY_KEYWORDS) + [DEFAULT_CATEGORY]
