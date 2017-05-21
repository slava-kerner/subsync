from pydub import AudioSegment
import numpy as np
import os
import audioop
import wave

import scipy.io.wavfile as wf


def convert(path_in, path_out):
    sound = AudioSegment.from_file(path_in)
    format_out = os.path.splitext(path_out)[1][1:]
    sound.export(path_out, format=format_out)


def make_mono(in_path, out_path):
    rate, data = wf.read(in_path)
    channels = len(data.shape)
    if channels == 2:
        data = np.mean(data, axis=1, dtype=data.dtype)
        channels = 1
    wf.write(out_path, rate, data)


def downsample(src_path, dst_path, inrate, outrate):
    """ changes framerate"""
    src = wave.open(src_path, 'r')
    src_data = src.readframes(src.getnframes())
    channels = src.getnchannels()
    print('channels:', channels)
    converted, _ = audioop.ratecv(src_data, 2, src.getnchannels(), inrate, outrate, None)

    dst = wave.open(dst_path, 'w')
    dst.setparams((channels, 2, outrate, 0, 'NONE', 'Uncompressed'))
    dst.writeframes(converted)

    src.close()
    dst.close()

