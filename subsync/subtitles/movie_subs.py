import os
import matplotlib.pyplot as plt
import logging
from matplotlib import collections as mc
import pylab as pl
from matplotlib.pyplot import cm
from tqdm import tqdm

from subsync.subtitles.subtitle import Subtitles
from subsync.subtitles.sub_signature import SubSignature


logger = logging.getLogger(__name__)


class MovieSubs:
    """ Set of subtitles corresponding to the same movie. """
    def __init__(self, movie=None, subs=None):
        """
        :param movie: Movie 
        :param subs: id -> {path, fps, lang}
        """
        self.movie = movie
        self.subs = subs

    def sub(self, sub_id):
        subtitle = self.subs[sub_id]
        return Subtitles.open(path=subtitle['path'], language=subtitle['lang'], fps=subtitle['fps'])

    @property
    def signatures(self):
        """ returns sub_id -> signature. """
        signatures = {}
        for sub_id, sub_props in self.subs.items():
            try:
                sub = Subtitles.open(path=sub_props['path'], language=sub_props['lang'], fps=sub_props['fps'])
            except:  # TODO FIX, some subs don't open, unicode issues
                continue
            sig = SubSignature(subtitle=sub)
            signatures[sub_id] = sig
        return signatures

    @property
    def signatures_with_labels(self):
        """ returns label -> signature. """
        signatures = self.signatures
        return {'%s_%s_%s' % (sub_id, self.subs[sub_id]['lang'], self.subs[sub_id]['fps']): sig for sub_id, sig in signatures.items()}

    @property
    def signature_distances(self):
        """ returns 2d dict."""
        signatures = self.signatures
        dist = {sub1: {sub2: sig1.dist(sig2) for sub2, sig2 in signatures.items()} for sub1, sig1 in signatures.items()}
        return dist

    def visualise_signature_distances(self):
        """ plots distances between, colored with green=identical, red=different. """
        dist = self.signature_distances
        ids = sorted(dist.keys())
        xs = []
        ys = []
        colors = []
        colormap = cm.ScalarMappable(cmap='RdYlGn', norm=plt.Normalize(vmin=0, vmax=1))
        for x, x_id in enumerate(ids):
            for y, y_id in enumerate(ids):
                xs.append(x)
                ys.append(y)
                score = 1 - dist[x_id][y_id]
                colors.append(colormap.to_rgba(score))
        plt.scatter(xs, ys, c=colors)
        plt.title('movie: "%s"' % self.movie.name)
        plt.show()

    def fit(self, ref_sig, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        signatures = self.signatures
        fitted_subs = {}
        for sub_id, sig in tqdm(signatures.items()):
            sub = self.sub(sub_id)
            a, b, dist = sig.fit(ref_sig, attempts=20)
            logger.debug('a=%f, b=%f, dist=%f', a, b, dist)
            sub = a * sub + b
            sub_info = self.subs[sub_id]
            out_path = os.path.join(output_folder, os.path.basename(sub_info['path']))
            sub.save(out_path)
            fitted_subs[sub_id] = sub_info.copy()
            fitted_subs[sub_id]['path'] = out_path
        return MovieSubs(movie=self.movie, subs=fitted_subs)
