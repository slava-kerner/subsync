import unittest
import os
from tempfile import TemporaryDirectory
from pydub import AudioSegment

import subsync.utils.audio


class TestAudio(unittest.TestCase):
    def test_convert(self):
        input_path = 'data/speech_9sec.mp3'
        with TemporaryDirectory() as folder:
            subsync.utils.audio.convert(input_path, os.path.join(folder, 'test.ogg'))
            subsync.utils.audio.convert(os.path.join(folder, 'test.ogg'), os.path.join(folder, 'test.wav'))
            subsync.utils.audio.convert(os.path.join(folder, 'test.wav'), os.path.join(folder, 'test.mp3'))
            length_orig = len(AudioSegment.from_file(input_path))
            length_processed = len(AudioSegment.from_file(os.path.join(folder, 'test.mp3')))
            self.assertLess(abs(length_orig - length_processed), 20)  # should be same length, but..
