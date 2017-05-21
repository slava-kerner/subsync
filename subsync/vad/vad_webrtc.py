import collections
import contextlib
import sys
import wave

import webrtcvad

from subsync.vad.vad import VAD
from subsync.subtitles.sub_signature import SubSignature


def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []
    intervals = []
    for frame in frames:
        # sys.stdout.write('1' if vad.is_speech(frame.bytes, sample_rate) else '0')
        if not triggered:
            ring_buffer.append(frame)
            num_voiced = len([f for f in ring_buffer if vad.is_speech(f.bytes, sample_rate)])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                start_time_ms = ring_buffer[0].timestamp * 1000
                # sys.stdout.write('+(%s)' % (ring_buffer[0].timestamp,))
                triggered = True
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            num_unvoiced = len([f for f in ring_buffer
                                if not vad.is_speech(f.bytes, sample_rate)])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                end_time_ms = (frame.timestamp + frame.duration) * 1000
                intervals += [(start_time_ms, end_time_ms)]
                # sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                # yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    # if triggered:
    #     sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    signature = SubSignature(intervals=intervals)
    return signature
    # print('WEBRTC:\n', signature)
    # if voiced_frames:
    #     yield b''.join([f.bytes for f in voiced_frames])


class VADWebrtc(VAD):
    def __init__(self, agressiveness=None, frame_duration_ms=None, padding_duration_ms=None):
        self.aggressiveness = agressiveness or 0
        self.frame_duration_ms = frame_duration_ms or 30
        self.padding_duration_ms = padding_duration_ms or 300
        self.vad = webrtcvad.Vad(self.aggressiveness)

    def _process(self, wave_input_filename):
        """ returns SubSignature. """
        audio, sample_rate = read_wave(wave_input_filename)

        frames = frame_generator(self.frame_duration_ms, audio, sample_rate)
        return vad_collector(sample_rate, self.frame_duration_ms, self.padding_duration_ms, self.vad, list(frames))
        # segments = vad_collector(sample_rate, self.frame_duration_ms, self.padding_duration_ms, self.vad, frames)
        # for i, segment in enumerate(segments):
        #     path = 'chunk-%002d.wav' % (i,)
            # print(' Writing %s' % (path,))
            # write_wave(path, segment, sample_rate)