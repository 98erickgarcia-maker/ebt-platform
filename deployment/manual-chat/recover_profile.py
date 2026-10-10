"""Remove only stale Chrome singleton symlinks while its dedicated container is stopped."""
import json
import os
from pathlib import Path
import subprocess

profile = Path('/var/lib/ebt-linux-chat-chrome')
if profile.is_symlink() or profile.resolve() != profile or not profile.is_dir():
    raise SystemExit('unexpected_profile_path')
containers = subprocess.check_output(['docker', 'ps', '-aq'], text=True).split()
for container_id in containers:
    data = json.loads(subprocess.check_output(['docker', 'inspect', container_id], text=True))[0]
    if data['State']['Running'] and any(Path(m.get('Source', '/')).resolve() == profile
                                     for m in data.get('Mounts', [])):
        raise SystemExit('profile_still_used_by_running_container')
for name in ('SingletonLock', 'SingletonSocket', 'SingletonCookie'):
    target = profile / name
    if target.parent.resolve() != profile:
        raise SystemExit('unexpected_lock_parent')
    if os.path.lexists(target):
        if not target.is_symlink():
            raise SystemExit('unexpected_regular_lock_preserved')
        target.unlink()  # Unlink this exact symlink, never its target or profile data.
print('stale_singleton_links_recovered_profile_preserved')
