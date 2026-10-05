"""Build, check, and publish reviewed content to the GitHub Pages branch."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOTE = 'https://github.com/voice-uxlab/pages.git'

def run(*args, cwd=ROOT):
    subprocess.run(args, cwd=cwd, check=True)

run(sys.executable, 'scripts/build.py')
run(sys.executable, 'scripts/check.py')
with tempfile.TemporaryDirectory(prefix='voice-uxlab-publish-') as directory:
    checkout = Path(directory) / 'site'
    run('git', 'clone', '--single-branch', '--branch', 'gh-pages', REMOTE, str(checkout))
    for item in checkout.iterdir():
        if item.name == '.git': continue
        if item.is_dir(): shutil.rmtree(item)
        else: item.unlink()
    shutil.copytree(ROOT / 'dist', checkout, dirs_exist_ok=True)
    run('git', 'add', '--all', cwd=checkout)
    changed = subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=checkout)
    if changed.returncode == 0:
        print('Published content is already up to date.')
    elif changed.returncode == 1:
        run('git', 'commit', '-m', 'Update Voice UX Lab archive', cwd=checkout)
        run('git', 'push', 'origin', 'gh-pages', cwd=checkout)
        print('Uploaded. Verify the GitHub Pages build before announcing publication.')
    else:
        changed.check_returncode()
