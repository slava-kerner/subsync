import os
from tempfile import TemporaryDirectory
import subsync.utils.audio


MIN_DIST_TO_DENSIFY_MS = 1000  # 2 items in signature closer than this will be glued into 1 item


class VAD:
    def process(self, audio_filename):
        # with TemporaryDirectory() as folder:
        if not audio_filename.endswith('wav'):
            fixed_audio_filename = audio_filename[:-3] + 'wav'
            subsync.utils.audio.convert(audio_filename, fixed_audio_filename)
            audio_filename = fixed_audio_filename

        sig = self._process(audio_filename)
        sig = sig.densify(MIN_DIST_TO_DENSIFY_MS)
        return sig

    def _process(self, wave_input_filename):
        raise NotImplementedError
