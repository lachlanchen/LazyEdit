import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from lazyedit.music_publish import package_music_publish


class MusicPackageSourceTests(unittest.TestCase):
    def test_public_source_survives_into_uploaded_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audio, video = root / 'song.mp3', root / 'art.mp4'
            audio.write_bytes(b'audio fixture')
            video.write_bytes(b'video fixture')
            with patch('lazyedit.music_publish._prepare_shipinhao_audio', return_value=audio), \
                    patch('lazyedit.music_publish._render_youtube_music_video', return_value=video):
                result = package_music_publish(
                    audio_path=audio, title='Song', output_root=root / 'packages',
                    lyrics_text='Corrected lyric', source_url='https://fun.lazying.art/#song',
                )
            with zipfile.ZipFile(result['zip_path']) as archive:
                name = Path(result['metadata_path']).name
                metadata = json.loads(archive.read(name))
            self.assertEqual(metadata['source_url'], 'https://fun.lazying.art/#song')
            self.assertTrue(metadata['published_elsewhere'])
            self.assertEqual(metadata['plain_lyrics'], 'Corrected lyric')


if __name__ == '__main__':
    unittest.main()
