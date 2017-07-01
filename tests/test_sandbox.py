import unittest
import os
from glob import glob
import json
import warnings
from tqdm import tqdm
from collections import OrderedDict
from tempfile import TemporaryDirectory

from pysrt import SubRipFile
from pydub import AudioSegment

from tests.test_utils import run_integration_tests
from subsync.subtitles.opensubtitles import OSCrawler, SubsOrganizer
import subsync.subtitles.sub_signature
from subsync.subtitles.sub_signature import SubSignature
from subsync.subtitles.subtitle import Subtitles
from subsync.utils.audio import make_mono, downsample
from subsync.download.youtube_downloader import YoutubeDownloader
from subsync.vad.vad_marsbroshok import VADMarsbroshok
from subsync.vad.vad_webrtc import VADWebrtc
from subsync.subtitles.opensubtitles import SubsOrganizer
from subsync.subtitles.movie_subs import MovieSubs
from subsync.movies.movie import Movie


youtube_test_config = {'format': 'bestaudio/best', 'quiet': True}

base_folder = '/home/slava/data/subs'

movies = {
    'persona': {
        'imdb_id': '0060827',
        'youtube': ['ySa4fK9SqII', 'rNj-giwqn8c', 'RuBbvBPYCDU'],
    },
    'once lived a singing blackbird': {
        'imdb_id': '0151035',
        'youtube': ['kpGZe_S6KWk', 'J9tutemoudU', 'QICFqs3r9dk']
    }
}

name = 'once lived a singing blackbird'

video_folder = os.path.join(base_folder, name, 'video')
audio_folder = os.path.join(base_folder, name, 'audio')
vad_folder = os.path.join(base_folder, name, 'vad')
sub_folder = os.path.join(base_folder, name, 'subs')


class Subs(unittest.TestCase):
    movie = Movie(name=name, imdb_id=movies[name]['imdb_id'])

    def test_download(self):
        crawler = OSCrawler(download_folder=sub_folder)
        crawler.imdb_id_to_os_id(movies[name]['imdb_id'])
        subs = crawler.imdb_id_to_subs(movies[name]['imdb_id'])
        print('sub_id:', subs)
        crawler.download(subs)
        SubsOrganizer().process_folder(sub_folder, sub_folder)

    def test_get_subs(self):
        # subs_folder = '/home/slava/data/subs'
        # TODO download
        subs_index = SubsOrganizer().process_folder(sub_folder, sub_folder)
        subs = MovieSubs(movie=self.movie, subs=subs_index)
        subsync.subtitles.sub_signature.plot(subs.signatures_with_labels)
        subs.visualise_signature_distances()

        # select reference signature:
        ref_from_audio = True
        if ref_from_audio:
            id = movies[name]['youtube'][0]
            agressiveness = 3
            ref_sig = SubSignature.read(os.path.join(vad_folder, 'webrtc%s_%s.txt' % (agressiveness, id)))
        else:  # from some other sub
            some_sub_id = list(subs.signatures.keys())[0]
            ref_sig = SubSignature(subtitle=subs.sub(some_sub_id))

        # fit:
        fitted_folder = os.path.join(base_folder, 'fitted')
        fitted = subs.fit(ref_sig, fitted_folder)
        with open(os.path.join(fitted_folder, 'subs.json'), 'w') as f:
            json.dump(fitted.subs, f, indent=4, sort_keys=True)

        # visualise fitted:
        subsync.subtitles.sub_signature.plot(fitted.signatures_with_labels)
        fitted.visualise_signature_distances()


# @unittest.skip('slow real test')
class Download(unittest.TestCase):
    def test_download_audio(self):
        downloader = YoutubeDownloader(youtube_test_config)
        for id in tqdm(movies[name]['youtube'], desc='downloading all audios'):
            path = os.path.join(audio_folder, '%s.wav' % id)
            downloader.download(id, path)

    def test_download_video(self):
        downloader = YoutubeDownloader({})
        for id in tqdm(movies[name]['youtube'], desc='downloading all videos'):
            downloader.download(id, os.path.join(video_folder, '%s.mp4' % id))


# @unittest.skip('slow real test')
class VAD(unittest.TestCase):
    def test_vad(self):
        signature = dict()
        dest_rate = 8000
        for id in tqdm(movies[name]['youtube'], desc='VAD'):
            cropped_path = os.path.join(audio_folder, 'crop_%s.wav' % id)
            if not os.path.exists(cropped_path):
                audio_path = os.path.join(audio_folder, '%s.wav' % id)
                audio = AudioSegment.from_file(audio_path)
                print('converting to wav:')
                audio[:100 * 60 * 1000].export(cropped_path, format='wav')

            downsampled_cropped_path = os.path.join(audio_folder, 'downsampled_crop_%s.wav' % id)
            if not os.path.exists(downsampled_cropped_path):
                print('downsampling from %s to %s:' % (audio.frame_rate, dest_rate))
                downsample(cropped_path, downsampled_cropped_path, audio.frame_rate, dest_rate)

            mono_downsampled_cropped_path = os.path.join(audio_folder, 'mono_downsampled_crop_%s.wav' % id)
            if not os.path.exists(mono_downsampled_cropped_path):
                print('making mono:')
                make_mono(downsampled_cropped_path, mono_downsampled_cropped_path)

            print('extracting signature:')
            output_path = os.path.join(audio_folder, 'mb_%s.txt' % id)
            if not os.path.exists(output_path):
                signature[id] = VADMarsbroshok().process(mono_downsampled_cropped_path)
                signature[id].write(output_path)

            for agressiveness in range(4):
                output_path = os.path.join(audio_folder, 'webrtc%s_%s.txt' % (agressiveness, id))
                if not os.path.exists(output_path):
                    signature[id] = VADWebrtc(agressiveness=agressiveness).process(mono_downsampled_cropped_path)
                    signature[id].write(output_path)

            # print('storing clips:')
            # clips_folder = os.path.join(base_folder, 'persona/audio/speech_clips/%s' % id)
            # print(signature[id])
            # signature[id].store_audio_clips(mono_downsampled_cropped_path, clips_folder)
        # VADMarsbroshok(audio_path).plot_detected_speech_regions()

    def test_visualise(self):
        signatures = OrderedDict()
        for sig_path in sorted(glob(os.path.join(vad_folder, '*.txt'))):
        # sig_path = os.path.join(base_folder, 'persona/audio/webrtc_signature_RuBbvBPYCDU.txt')
            label = os.path.splitext(os.path.basename(sig_path))[0]
            signatures[label] = SubSignature.read(sig_path)
        subsync.subtitles.sub_signature.plot(signatures)



@unittest.skip('slow real test')
class Fit(unittest.TestCase):
    def test_fit(self):
        warnings.simplefilter("ignore")
        index_path = os.path.join(base_folder, 'subs.json')
        with open(index_path) as f:
            index = json.load(f)

        for sub1_path, sub1_props in index.items():
            # print(Subtitles.open(path=sub1_path, language=sub1_lng))
            try:
                sub1 = Subtitles.open(path=sub1_path, language=sub1_props['lang'])
            except:
                continue
            sig1 = SubSignature(subtitle=sub1)
            for sub2_path, sub2_props in index.items():
                if sub1_path == sub2_path:
                    continue
                try:
                    sub2 = Subtitles.open(path=sub2_path, language=sub2_props['lang'])
                except:
                    continue
                sig2 = SubSignature(subtitle=sub2)
                a, b, dist = sig1.fit(sig2, attempts=10)
                fps1 = float(sub1_props['fps'])
                fps2 = float(sub2_props['fps'])
                expected_fps_ratio = fps1 / fps2 if fps1 != 0 and fps2 != 0 else None
                print('fitting %s to %s (expected fps ratio =%s): \ndist=%f, a=%f, b=%f' %
                      (sub1_path, sub2_path, expected_fps_ratio, dist, a, b))
