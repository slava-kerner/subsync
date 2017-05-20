import unittest

from subsync.vad.vad_marsbroshok import VADMarsbroshok

data_path = 'data/speech_9sec.wav'


class TestVADMarsbroshok(unittest.TestCase):
    def test_something(self):
        signature = VADMarsbroshok(data_path).signature()
        self.assertEqual(signature[0][0], 510)
        self.assertEqual(len(signature), 14)
