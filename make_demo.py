#!/usr/bin/env python3
"""Create an explicitly synthetic Git/error fixture; never reads another repo."""
import argparse
import os
import pathlib
import subprocess
from datetime import datetime, timedelta


def create_demo(destination):
    root = pathlib.Path(destination).resolve()
    if root.exists() and any(root.iterdir()):
        raise RuntimeError('Choose an empty directory for the synthetic demo repository.')
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    (root / 'README.md').write_text('# Synthetic SlothPulse demo\n\nAll commits, people, and errors here are demonstration fixtures, not a real work history.\n')
    (root / 'worker.py').write_text('def download_url(job):\n    return job["result"]["download_url"]\n\nif __name__ == "__main__":\n    print(download_url({"job_id": "demo-42"}))\n')
    anchor = datetime.now().astimezone().replace(hour=9, minute=0, second=0, microsecond=0)
    events = [
        (2, 'Teng Demo', 'chore: initialize sample export worker'),
        (1, 'Teng Demo', 'feat: parse CSV rows into records'),
        (1, 'Teng Demo', 'docs: describe expected export payload'),
        (0, 'Teng Demo', 'feat: queue CSV exports for background processing'),
        (0, 'Teng Demo', 'fix: handle empty export jobs without crashing'),
        (0, 'Teng Demo', 'test: cover empty export jobs'),
        (0, 'Teng Demo', 'docs: add local worker startup instructions'),
        (0, 'Teng Demo', 'fix: preserve export job IDs across retries'),
        (0, 'Kai Demo', 'chore: add sample worker configuration'),
    ]
    for index, (days, author, subject) in enumerate(events):
        with (root / 'changes.txt').open('a') as notes:
            notes.write(subject + '\n')
        subprocess.run(['git', 'add', '.'], cwd=root, check=True)
        env = dict(os.environ)
        date = (anchor - timedelta(days=days) + timedelta(minutes=index)).isoformat()
        env.update(GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        subprocess.run(['git', '-c', 'user.name=' + author, '-c', 'user.email=demo@example.invalid',
                        '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null',
                        'commit', '-qm', subject], cwd=root, env=env, check=True)
    error = subprocess.run(['python3', 'worker.py'], cwd=root, capture_output=True, text=True)
    assert error.returncode != 0
    trace = 'EXPORT_API_KEY=demo_fixture_key_not_a_real_credential_12345\n' + error.stderr.replace(str(root) + '/', '')
    (root / 'error.txt').write_text(trace, encoding='utf-8')
    return root


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', help='An empty destination directory, e.g. /tmp/slothpulse-demo')
    args = parser.parse_args()
    print(create_demo(args.destination))
