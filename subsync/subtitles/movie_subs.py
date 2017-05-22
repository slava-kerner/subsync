import os
import matplotlib.pyplot as plt
from matplotlib import collections as mc
import pylab as pl
from matplotlib.pyplot import cm

from subsync.subtitles.subtitle import Subtitles
from subsync.subtitles.sub_signature import SubSignature


class MovieSubs:
    """ Set of subtitles corresponding to the same movie. """
    def __init__(self, movie=None, subs=None):
        """
        :param movie: Movie 
        :param subs: id -> {path, fps, lang}
        """
        self.movie = movie
        self.subs = subs

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
