"""Operator-authorized public Vancouver fixture, once per private workspace.

No owner library, metadata, platform account or queue is imported. The read-only
sample source stays outside the image. Only one canonical editable source is
retained per workspace; subsequent startups reuse it and the existing DB row.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil

from lazyedit import db


def main():
    source = Path('/samples/vancouver.mp4')
    expected = os.environ.get('LAZYEDIT_SAMPLE_SHA256', '')
    if not source.is_file() or not expected:
        return
    with source.open('rb') as sample:
        if hashlib.file_digest(sample, 'sha256').hexdigest() != expected:
            raise RuntimeError('Authorized sample changed; operator review required')
    directory = Path('/state/data/studio_sample_vancouver')
    directory.mkdir(exist_ok=True)
    destination = directory / 'vancouver.mp4'
    if not destination.exists():
        stage = directory / 'vancouver.part'
        with source.open('rb') as input_file, stage.open('wb') as output:
            # Reflink when the local filesystem permits it; never require it.
            try:
                import fcntl
                fcntl.ioctl(output.fileno(), 0x40049409, input_file.fileno())
            except OSError:
                shutil.copyfileobj(input_file, output, 1024 * 1024)
        stage.replace(destination)
    db.ensure_schema()
    video_id = db.add_video(str(destination), '温哥华，先看海还是先吃？ · Vancouver sample', 'upload')
    Path('/state/studio/sample.json').write_text(json.dumps({
        'videoId': video_id, 'sha256': expected, 'filename': 'vancouver.mp4'}))
    print('Authorized Vancouver sample is available in this workspace.')


if __name__ == '__main__':
    main()
