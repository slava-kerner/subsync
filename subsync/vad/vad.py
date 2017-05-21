import os
from tempfile import TemporaryDirectory
import subsync.utils.audio


class VAD:
    def process(self, audio_filename):
        # with TemporaryDirectory() as folder:
        if not audio_filename.endswith('wav'):
            fixed_audio_filename = audio_filename[:-3] + 'wav'
            subsync.utils.audio.convert(audio_filename, fixed_audio_filename)
            audio_filename = fixed_audio_filename

        return self._process(audio_filename)

    def _process(self, wave_input_filename):
        raise NotImplementedError
