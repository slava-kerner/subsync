from pydub import AudioSegment
import os


def convert(path_in, path_out):
    sound = AudioSegment.from_file(path_in)
    format_out = os.path.splitext(path_out)[1][1:]
    sound.export(path_out, format=format_out)
